# PDF Invoice Generator

A Python document-automation tool that generates PDF invoices from structured CSV or JSON data and reusable HTML templates.

The project demonstrates a complete document-processing pipeline:

```mermaid
flowchart LR
    A["CSV or JSON data"] --> B["Python parser"]
    B --> C["HTML template"]
    C --> D["Rendered invoice"]
    D --> E["PDF document"]
```

## Business Use Case

Creating invoices manually is repetitive and error-prone.

This application separates:

* Source data
* Document layout
* PDF generation

The same invoice data can be rendered with different templates, while one template can be reused for many invoice records.

## Key Features

* Read invoice records from CSV
* Read invoice records from JSON
* Select a source file interactively
* Select an invoice by its identifier
* Choose between multiple HTML layouts
* Replace template placeholders with structured data
* Generate PDF documents with WeasyPrint
* Support Cyrillic text through Unicode-compatible fonts
* Save generated documents in a dedicated output directory
* Open the generated PDF in the operating system’s default viewer

## Included Templates

The repository contains three layouts:

* Classic
* Minimal
* Modern

Templates use placeholders such as:

```html
{{invoice_id}}
{{customer_name}}
{{item_name}}
{{grand_total}}
```

Values are replaced with data from the selected CSV or JSON record.

## Example Input

```csv
invoice_id,date,customer_name,item_name,quantity,unit_price,total,tax,grand_total
INV-001,2025-01-15,Ivan Petrov,Laptop,1,45000,45000,8100,53100
```

Example JSON data can use the same field names.

## Tech Stack

* Python
* pandas
* WeasyPrint
* HTML
* CSS
* CSV
* JSON
* pathlib

## Project Structure

```text
pdf-checkmaker/
├── data/
│   ├── invoices.csv
│   └── invoices.json
├── templates/
│   ├── invoice_classic.html
│   ├── invoice_minimal.html
│   └── invoice_modern.html
├── demo_interactive.py
├── invoice_generator.py
├── requirements.txt
└── README.md
```

Generated PDF files are written to:

```text
output/
```

The output directory and PDF files are excluded from Git.

## Getting Started

### Requirements

* Python 3.10 or newer
* pip
* System dependencies required by WeasyPrint

### Installation

```bash
git clone https://github.com/TatsianaU/pdf-checkmaker.git
cd pdf-checkmaker
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the interactive generator:

```bash
python invoice_generator.py
```

The application will ask you to:

1. Select a CSV or JSON source file
2. Select an HTML template
3. Select an invoice ID
4. Generate the PDF
5. Open the completed document

Run the automatic demonstration:

```bash
python demo_interactive.py
```

The demonstration selects the first available data file, template, and invoice record and generates a sample PDF.

## Supported Fields

The included sample data uses:

| Field              | Purpose            |
| ------------------ | ------------------ |
| `invoice_id`       | Invoice identifier |
| `date`             | Invoice date       |
| `customer_name`    | Customer name      |
| `customer_email`   | Customer email     |
| `customer_address` | Billing address    |
| `item_name`        | Product or service |
| `quantity`         | Quantity           |
| `unit_price`       | Price per unit     |
| `total`            | Amount before tax  |
| `tax`              | Tax amount         |
| `grand_total`      | Final amount       |

The generator also recognizes several common alternatives for an invoice identifier, including `id`, `invoice_number`, and `number`.

## Cross-Platform Behavior

The application contains separate commands for opening generated PDFs on:

* Windows
* macOS
* Linux

It also includes Windows-specific console encoding handling for Unicode and Cyrillic text.

## Current Status

This is a functional document-automation prototype.

Possible future improvements include a web interface, batch generation, stronger schema validation, automated tests, and support for additional document types.
