# 💎 Jewelry Inventory Automation

A functional Flask prototype for barcode-based jewelry identification, inventory adjustment, label generation, and restocking support with Shopify integration.

IU International University of Applied Sciences · DLBCCOEDAH01 · Project: Digitalization and Automation Hackathon

---

## 🎯 Project objective

This repository implements a prototype for reducing repetitive manual work in a jewelry shop. Staff can identify an item from its existing 8-digit barcode, retrieve the associated product data, adjust inventory, prepare printable labels, and review simple restocking recommendations from one interface.

The prototype provides two data modes:

- **Demo mode:** runs locally with fictional jewelry products and generated product images.
- **Shopify API mode:** retrieves product and inventory information from Shopify using the product variant barcode as the primary identifier.

> The prototype focuses on the Phase 2 implementation: converting the proposed To-Be process into a working proof of concept that can be demonstrated and evaluated.

## 🧭 Workflow at a glance

```text
                         8-digit barcode
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Flask web interface  │
                    │ scan · select · edit │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Data source          │
                    │ Demo / Shopify API   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       Product lookup    Inventory update   Sales history
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Automation outputs   │
                    │ labels · restocking  │
                    └──────────────────────┘
```

### Request flow

1. A barcode is entered manually or with a barcode scanner.
2. The application validates that it contains exactly eight numeric digits.
3. Demo mode searches the bundled sample catalogue; API mode queries Shopify.
4. Product information is displayed together with the current inventory quantity.
5. Inventory changes remain proposed locally until **Publish inventory** is selected.
6. Selected products can be rendered as small fold-over PDF tags or A4 box-label sheets.
7. The restocking view combines current inventory and six-month sales data to calculate a suggested order quantity.

## 🧩 Application components

| Component | Responsibility | Design rationale |
| --- | --- | --- |
| Flask | Web application and API routes | Small, readable Python backend suitable for a prototype |
| Shopify Admin GraphQL API | Product, inventory and order data | Integrates with the shop's existing commerce platform |
| Demo catalogue | Offline demonstration data | Makes the complete workflow reproducible without credentials |
| ReportLab | PDF and Code 128 generation | Produces physical-size printable labels directly in Python |
| HTML / CSS / JavaScript | Browser interface | Keeps scanning, inventory, printing and restocking in one workflow |
| python-dotenv | Local configuration | Keeps Shopify credentials outside source code |

## 🗂️ Repository structure

```text
jewelry_inventory_phase2/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── services/
│   ├── demo_data.py
│   ├── inventory.py
│   ├── labels.py
│   └── shopify.py
├── static/
│   ├── app.js
│   ├── style.css
│   └── demo/             # fictional demo product images
├── templates/
│   └── index.html
└── generated/
```

## ✨ Prototype highlights

| Area | Implementation |
| --- | --- |
| Identification | Exact 8-digit barcode lookup; leading zeroes remain valid |
| Demo | Ten fictional jewelry variants with images, prices, stock and sales history |
| Shopify | Barcode-based variant lookup through the Admin GraphQL API |
| Inventory | `+` / `-` proposed quantity followed by an explicit publish action |
| Small tags | **50 × 12 mm PDF**, one physical fold-over tag per PDF page |
| Tag preview | Browser PDF preview before downloading or printing |
| Box labels | Configurable A4 PDF sheet with product image, price and Code 128 barcode |
| Restocking | Six-month sales average, coverage target and safety factor |
| Security | Secrets loaded from `.env`; credentials are not intended for Git |

## 🏷️ Small fold-over PDF tags

The small jewelry tag is deliberately generated as a PDF rather than relying on a Zebra-specific command file.

Each PDF page is **50 × 12 mm** and represents one physical fold-over adhesive tag:

```text
┌───────────────────────┬───────────────────────┐
│      CODE 128         │       79.90 EUR       │
│      10010101         │    Solitaire Ring     │
│                       │   Gold · Size 54      │
└───────────────────────┴───────────────────────┘
       barcode face             product face
```

The browser can preview the generated PDF before it is downloaded. Printing should use **Actual Size / 100% scale** so the physical dimensions are preserved. A compatible Zebra printer can print the PDF through its operating-system printer driver; the output is not tied to a specific Zebra command language.

## 🖼️ A4 box labels

Box labels remain a separate A4 workflow. Each label can include:

- product name and variant;
- demo or Shopify product image;
- inventory marker;
- price;
- Code 128 barcode;
- exact 8-digit human-readable barcode.

Rows and columns are configurable so the prototype can be adapted to different pre-cut A4 sticker sheets.

## 📦 Restocking logic

The prototype uses a deliberately simple and explainable rule:

```text
average monthly sales = sold during previous 6 months / 6

target stock =
ceil(average monthly sales × months of coverage × safety factor)

recommended order =
max(0, target stock - current inventory)
```

Default configuration:

```text
months of coverage = 3
safety factor      = 1.20
```

This is intended as a transparent proof-of-concept rule rather than a production demand-forecasting model.

## 🚀 Run locally

### Prerequisites

- Python 3.10+
- `pip`
- a modern web browser
- Shopify credentials only if API mode is required

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the application

Copy the example environment file:

```bash
cp .env.example .env
```

For a credentials-free demonstration:

```env
DATA_MODE=demo
```

For Shopify API mode, add the shop domain, client ID and client secret to the local `.env` file. Never commit the real `.env` file.

### 4. Start Flask

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

## ✅ Demo workflow

Demo mode can be tested immediately. Example barcodes include:

```text
10010101  Solitaire Ring - Gold, Size 54
20014101  Drop Earrings - Gold
40022001  Jupiter Necklace - Steel
80066001  Classic Hoops - Gold
```

A typical demonstration is:

1. Select **Demo**.
2. Scan or click `10010101`.
3. Adjust its proposed inventory with `+` or `-`.
4. Publish the inventory change.
5. Open **Labels & Printing**.
6. Preview the 50 × 12 mm fold-over PDF.
7. Download the same PDF if required.
8. Open **Restocking** to review the calculated order recommendation.

## 🔐 Security by design

The repository contains `.env.example`, not production credentials. Shopify secrets should exist only in the local `.env` file, which is ignored by Git.

Before publishing the repository, verify:

```bash
git status
git check-ignore .env
```

If a real credential has ever been exposed publicly or shared outside its intended environment, rotate it before using the repository.

## ⚖️ Design decisions and trade-offs

### Why barcode instead of SKU?

The shop workflow uses physical 8-digit barcodes while Shopify SKU values may be empty. The barcode is therefore treated as the primary lookup identifier throughout the prototype.

### Why PDF for the small tag?

PDF gives staff a visible preview and works through a normal printer-driver workflow. It also preserves the intended physical page size. This makes the prototype less dependent on one Zebra model or printer language while still allowing a Zebra label printer to be used.

### Why keep a Demo mode?

The project can be evaluated without access to the live store or credentials. The same interface and main automation steps can therefore be demonstrated safely and repeatedly.

### What would be added in production?

- supplier API integration and purchase-order generation;
- forecasting based on longer sales history and seasonality;
- explicit multi-location inventory selection;
- authentication and staff roles;
- persistent database storage for scan sessions and audit history;
- printer calibration profiles for the exact label stock and Zebra model;
- automated tests and deployment pipeline.

## 📌 Portfolio alignment

The prototype provides implementation evidence for the Phase 2 portfolio through:

- a working barcode-based To-Be process;
- a selectable offline demonstration and live Shopify integration;
- inventory adjustment with explicit publication;
- automated PDF label generation;
- a restocking calculation based on sales and stock data;
- a structure that can be tested against identification time, label-generation time, inventory-record errors, low-stock detection lag, and manual product lookups.

No baseline KPI measurements are fabricated in the repository; measurements can be recorded during prototype testing.

## 👤 Author

**ApteryxDev**

Bachelor of Applied Artificial Intelligence  
IU International University of Applied Sciences
