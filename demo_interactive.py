#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт с симуляцией интерактивного выбора
"""

import os
import sys
import platform
from pathlib import Path
from io import StringIO

# Настройка кодировки для Windows консоли
if platform.system() == 'Windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.system('chcp 65001 > nul 2>&1')

# Подавляем предупреждения GLib на Windows
if platform.system() == 'Windows':
    os.environ['GLIB_AVAILABLE_SCHEMAS'] = ''
    os.environ['GSETTINGS_SCHEMA_DIR'] = ''
    os.environ['GIO_USE_VFS'] = 'local'
    os.environ['GSETTINGS_BACKEND'] = 'memory'

import warnings
warnings.filterwarnings('ignore')

from invoice_generator import InvoiceGenerator

def demo_generation():
    """Демонстрация генерации PDF с автоматическим выбором"""
    
    print("\n" + "="*60)
    print("  🎬 ДЕМОНСТРАЦИЯ ГЕНЕРАТОРА PDF")
    print("="*60 + "\n")
    
    generator = InvoiceGenerator()
    
    # Получаем списки файлов
    data_files = generator.get_data_files()
    template_files = generator.get_template_files()
    
    print("🔹 Шаг 1: Выбираем файл данных")
    print(f"   Доступно файлов: {len(data_files)}")
    for i, f in enumerate(data_files, 1):
        print(f"   {i}. {f.name}")
    
    # Автоматически выбираем первый файл
    selected_data_file = data_files[0]
    print(f"\n   ✅ Выбран: {selected_data_file.name}")
    
    # Читаем данные
    data = generator.read_data_file(selected_data_file)
    print(f"   📊 Загружено записей: {len(data)}")
    
    print("\n🔹 Шаг 2: Выбираем шаблон")
    print(f"   Доступно шаблонов: {len(template_files)}")
    for i, f in enumerate(template_files, 1):
        print(f"   {i}. {f.name}")
    
    # Автоматически выбираем первый шаблон
    selected_template_file = template_files[0]
    print(f"\n   ✅ Выбран: {selected_template_file.name}")
    
    # Читаем шаблон
    template = generator.read_template(selected_template_file)
    
    print("\n🔹 Шаг 3: Выбираем чек")
    invoice_ids = generator.get_invoice_ids(data)
    print(f"   Доступно чеков: {len(invoice_ids)}")
    for i, invoice_id in enumerate(invoice_ids[:3], 1):  # Показываем первые 3
        print(f"   {i}. {invoice_id}")
    if len(invoice_ids) > 3:
        print(f"   ... и еще {len(invoice_ids) - 3}")
    
    # Автоматически выбираем первый чек
    selected_invoice_id = invoice_ids[0]
    print(f"\n   ✅ Выбран: {selected_invoice_id}")
    
    invoice_data = generator.find_invoice_by_id(data, selected_invoice_id)
    
    print("\n🔹 Шаг 4: Генерируем PDF")
    html_content = generator.render_template(template, invoice_data)
    
    output_filename = f"demo_{selected_invoice_id}.pdf"
    output_path = generator.output_dir / output_filename
    
    print(f"   ⏳ Создаём PDF...")
    
    if generator.generate_pdf(html_content, output_path):
        size_kb = output_path.stat().st_size / 1024
        print(f"   ✅ PDF создан: {output_filename} ({size_kb:.1f} KB)")
        print(f"   📁 Путь: {output_path}")
        
        # Открываем PDF
        print(f"\n🔹 Шаг 5: Открываем PDF")
        generator.open_pdf(output_path)
        print(f"   ✅ PDF открыт в системной программе")
    else:
        print(f"   ❌ Ошибка создания PDF")
    
    print("\n" + "="*60)
    print("  ✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*60 + "\n")
    
    print("💡 Теперь попробуйте интерактивный режим:")
    print("   python invoice_generator.py")
    print()

if __name__ == "__main__":
    try:
        demo_generation()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

