#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Invoice Generator
Генератор PDF-чеков из CSV/JSON данных с использованием HTML-шаблонов
"""

import os
import sys
import json
import csv
import platform
import subprocess
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

# Настройка кодировки для Windows консоли
if platform.system() == 'Windows':
    # Устанавливаем UTF-8 для консоли
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Для старых версий Python
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    # Устанавливаем кодовую страницу консоли на UTF-8
    os.system('chcp 65001 > nul 2>&1')

# Подавляем предупреждения GLib на Windows
if platform.system() == 'Windows':
    os.environ['GLIB_AVAILABLE_SCHEMAS'] = ''
    os.environ['GSETTINGS_SCHEMA_DIR'] = ''
    os.environ['GIO_USE_VFS'] = 'local'
    os.environ['GSETTINGS_BACKEND'] = 'memory'
    
# Подавляем все предупреждения от библиотек
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)


class SuppressStderr:
    """Context manager для подавления stderr (используется для GLib предупреждений)"""
    
    def __enter__(self):
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        self.save_fd = os.dup(2)
        os.dup2(self.null_fd, 2)
        return self
    
    def __exit__(self, *_):
        os.dup2(self.save_fd, 2)
        os.close(self.null_fd)
        os.close(self.save_fd)


# Импортируем pandas и WeasyPrint с подавлением stderr на Windows
if platform.system() == 'Windows':
    with SuppressStderr():
        import pandas as pd
        from weasyprint import HTML, CSS
        import logging
else:
    import pandas as pd
    from weasyprint import HTML, CSS
    import logging

# Отключаем логирование WARNING от WeasyPrint и связанных библиотек
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)


class InvoiceGenerator:
    """Класс для генерации PDF-чеков из данных и HTML-шаблонов"""
    
    def __init__(self, data_dir: str = "data", templates_dir: str = "templates", output_dir: str = "output"):
        self.data_dir = Path(data_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        
        # Создаем директории если они не существуют
        self.output_dir.mkdir(exist_ok=True)
        
    def get_data_files(self) -> List[Path]:
        """Получить список всех CSV и JSON файлов в директории данных"""
        if not self.data_dir.exists():
            return []
        
        data_files = []
        for ext in ['*.csv', '*.json']:
            data_files.extend(self.data_dir.glob(ext))
        
        return sorted(data_files)
    
    def get_template_files(self) -> List[Path]:
        """Получить список всех HTML-шаблонов"""
        if not self.templates_dir.exists():
            return []
        
        return sorted(self.templates_dir.glob('*.html'))
    
    def read_csv_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Читает CSV файл и возвращает список словарей"""
        try:
            # Используем pandas для чтения CSV
            df = pd.read_csv(file_path)
            # Конвертируем в список словарей
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ Ошибка при чтении CSV файла {file_path}: {e}")
            return []
    
    def read_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Читает JSON файл и возвращает данные"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Если данные - список, возвращаем как есть
                if isinstance(data, list):
                    return data
                # Если словарь - оборачиваем в список
                elif isinstance(data, dict):
                    return [data]
                else:
                    return []
        except Exception as e:
            print(f"❌ Ошибка при чтении JSON файла {file_path}: {e}")
            return []
    
    def read_data_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Универсальный метод для чтения файла данных"""
        if file_path.suffix.lower() == '.csv':
            return self.read_csv_file(file_path)
        elif file_path.suffix.lower() == '.json':
            return self.read_json_file(file_path)
        else:
            print(f"❌ Неподдерживаемый формат файла: {file_path}")
            return []
    
    def get_invoice_ids(self, data: List[Dict[str, Any]]) -> List[str]:
        """Извлекает список invoice_id из данных"""
        invoice_ids = []
        for record in data:
            # Ищем поле invoice_id (с различными вариациями названия)
            for key in ['invoice_id', 'invoiceId', 'id', 'invoice_number', 'number']:
                if key in record:
                    invoice_ids.append(str(record[key]))
                    break
        return invoice_ids
    
    def find_invoice_by_id(self, data: List[Dict[str, Any]], invoice_id: str) -> Optional[Dict[str, Any]]:
        """Находит чек по invoice_id"""
        for record in data:
            for key in ['invoice_id', 'invoiceId', 'id', 'invoice_number', 'number']:
                if key in record and str(record[key]) == invoice_id:
                    return record
        return None
    
    def read_template(self, template_path: Path) -> str:
        """Читает HTML-шаблон"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Ошибка при чтении шаблона {template_path}: {e}")
            return ""
    
    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Подставляет данные в HTML-шаблон"""
        # Простая замена плейсхолдеров вида {{variable}}
        result = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    def generate_pdf(self, html_content: str, output_path: Path) -> bool:
        """Генерирует PDF из HTML-контента"""
        try:
            # CSS для поддержки кириллицы
            css = CSS(string='''
                @font-face {
                    font-family: 'DejaVu Sans';
                    src: local('DejaVu Sans');
                }
                body {
                    font-family: 'DejaVu Sans', 'Roboto', Arial, sans-serif;
                }
            ''')
            
            # Подавляем stderr на Windows для GLib предупреждений
            if platform.system() == 'Windows':
                with SuppressStderr():
                    HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
            else:
                HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
            
            return True
        except Exception as e:
            print(f"❌ Ошибка при генерации PDF: {e}")
            return False
    
    def open_pdf(self, pdf_path: Path):
        """Открывает PDF в системной программе"""
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(str(pdf_path))
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', str(pdf_path)])
            else:  # Linux
                subprocess.run(['xdg-open', str(pdf_path)])
        except Exception as e:
            print(f"❌ Не удалось открыть PDF: {e}")
            print(f"📄 PDF сохранен: {pdf_path}")
    
    def display_menu(self, items: List[Any], title: str) -> int:
        """Отображает меню и возвращает выбор пользователя (возвращает индекс или -1 для выхода)"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        
        if not items:
            print("  ⚠️  Нет доступных элементов")
            return -1
        
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item}")
        
        print(f"{'='*60}")
        
        while True:
            try:
                choice = input(f"Выберите пункт (1-{len(items)}) или '0' для выхода: ").strip()
                choice_num = int(choice)
                
                if choice_num == 0:
                    return -1  # Возвращаем -1 для выхода
                
                if 1 <= choice_num <= len(items):
                    return choice_num - 1  # Возвращаем индекс (0-based)
                else:
                    print(f"❌ Введите число от 1 до {len(items)}")
            except ValueError:
                print("❌ Введите корректное число")
            except KeyboardInterrupt:
                print("\n\n👋 Выход...")
                sys.exit(0)
    
    def run(self):
        """Основной цикл работы программы"""
        print("\n" + "="*60)
        print("  🧾 ГЕНЕРАТОР PDF-ЧЕКОВ")
        print("="*60)
        
        # 1. Получаем список файлов данных
        data_files = self.get_data_files()
        if not data_files:
            print(f"\n❌ Нет файлов данных в директории '{self.data_dir}'")
            print("   Создайте CSV или JSON файлы с данными чеков")
            return
        
        # 2. Получаем список шаблонов
        template_files = self.get_template_files()
        if not template_files:
            print(f"\n❌ Нет HTML-шаблонов в директории '{self.templates_dir}'")
            print("   Создайте HTML-шаблон для чека")
            return
        
        # 3. Пользователь выбирает файл данных
        choice = self.display_menu(
            [f.name for f in data_files],
            "ДОСТУПНЫЕ ФАЙЛЫ ДАННЫХ"
        )
        
        if choice == -1:
            print("\n👋 До свидания!")
            return
        
        selected_data_file = data_files[choice]
        print(f"\n✅ Выбран файл: {selected_data_file.name}")
        
        # 4. Читаем данные
        data = self.read_data_file(selected_data_file)
        if not data:
            print("❌ Не удалось прочитать данные из файла")
            return
        
        print(f"📊 Загружено записей: {len(data)}")
        
        # 5. Пользователь выбирает шаблон
        choice = self.display_menu(
            [f.name for f in template_files],
            "ДОСТУПНЫЕ ШАБЛОНЫ"
        )
        
        if choice == -1:
            print("\n👋 До свидания!")
            return
        
        selected_template_file = template_files[choice]
        print(f"\n✅ Выбран шаблон: {selected_template_file.name}")
        
        # 6. Читаем шаблон
        template = self.read_template(selected_template_file)
        if not template:
            print("❌ Не удалось прочитать шаблон")
            return
        
        # 7. Получаем список invoice_id
        invoice_ids = self.get_invoice_ids(data)
        if not invoice_ids:
            print("❌ Не найдено ни одного invoice_id в данных")
            return
        
        # 8. Пользователь выбирает invoice
        choice = self.display_menu(
            invoice_ids,
            "ДОСТУПНЫЕ ЧЕКИ (INVOICE ID)"
        )
        
        if choice == -1:
            print("\n👋 До свидания!")
            return
        
        selected_invoice_id = invoice_ids[choice]
        print(f"\n✅ Выбран чек: {selected_invoice_id}")
        
        # 9. Находим данные чека
        invoice_data = self.find_invoice_by_id(data, selected_invoice_id)
        if not invoice_data:
            print(f"❌ Не удалось найти данные для чека {selected_invoice_id}")
            return
        
        print(f"📋 Данные чека загружены")
        
        # 10. Генерируем HTML с подставленными данными
        html_content = self.render_template(template, invoice_data)
        
        # 11. Генерируем PDF
        output_filename = f"invoice_{selected_invoice_id}.pdf"
        output_path = self.output_dir / output_filename
        
        print(f"\n⏳ Генерация PDF...")
        if self.generate_pdf(html_content, output_path):
            print(f"✅ PDF успешно создан: {output_path}")
            
            # 12. Открываем PDF
            print(f"📂 Открываем PDF...")
            self.open_pdf(output_path)
        else:
            print(f"❌ Не удалось создать PDF")


def main():
    """Точка входа в программу"""
    try:
        generator = InvoiceGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

