# 💎 Jewelry Inventory Automation

> **Project: Digitalization and Automation Hackathon — DLBCCOEDAH01**  
> Bachelor of Applied Artificial Intelligence · IU International University

A lightweight inventory automation prototype designed for a real-world jewelry retail workflow.

The application connects product identification, Shopify inventory data, label generation, stock adjustment, and restocking support into a single browser-based interface.

---

## 🎯 Project Objective

Jewelry inventory management can involve a surprising amount of repetitive manual work.

Products stored individually in jewelry boxes need to be identified, matched with the correct product record, checked against inventory, labeled correctly, and eventually considered for restocking.

The objective of this prototype is to demonstrate how this workflow can be partially automated using:

- **8-digit barcode identification**
- **Shopify Admin API integration**
- **Automatic product and variant retrieval**
- **Inventory adjustment**
- **PDF jewelry-tag generation**
- **A4 product/box-label generation**
- **Sales-based restocking recommendations**
- **A self-contained Demo Mode for testing**

The prototype focuses on reducing repetitive product searches and manual label preparation while keeping a human operator in control of inventory changes.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔎 Barcode scanning | Identifies products using their exact 8-digit barcode |
| 🛍️ Shopify integration | Retrieves live product, variant, price, image and inventory information |
| 🧪 Demo Mode | Runs the complete prototype without Shopify credentials |
| 🖼️ Product images | Displays product images alongside scanned inventory |
| ➕ Inventory adjustment | Allows proposed stock changes before publishing |
| 🏷️ Jewelry tags | Generates small fold-over PDF tags for individual jewelry items |
| 📄 Box labels | Generates larger product labels arranged on configurable A4 sheets |
| 📊 Restocking | Calculates target stock and suggested reorder quantities |
| 🔐 Environment configuration | Keeps Shopify credentials outside the repository |

---

## 🏗️ Architecture at a Glance

```text
                        ┌──────────────────────┐
                        │      User / Staff    │
                        └──────────┬───────────┘
                                   │
                            Scan 8-digit barcode
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │        Flask Web App       │
                    │                            │
                    │  Scanning                  │
                    │  Inventory adjustment      │
                    │  Label generation          │
                    │  Restocking calculations   │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │    Demo Mode     │        │   Shopify API    │
          │                  │        │                  │
          │ Fictional data   │        │ Products         │
          │ Images           │        │ Variants         │
          │ Inventory        │        │ Inventory        │
          │ Sales history    │        │ Orders           │
          └────────┬─────────┘        └────────┬─────────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      PDF Generation      │
                    │                          │
                    │ Small jewelry tags       │
                    │ A4 box/product labels    │
                    └──────────────────────────┘
```

---

## 📸 Prototype in Action

### 🔎 Inventory Scanning

Products are identified through their **8-digit barcode**.

When running in Shopify API mode, the application searches the corresponding Shopify variant and retrieves information such as:

- Product name
- Variant/options
- Barcode
- Price
- Product image
- Current inventory quantity

Inventory adjustments can then be prepared using the `+` and `−` controls.

Changes are not immediately written to Shopify. The user first defines the proposed quantity and explicitly selects **Publish inventory**.

![Inventory scanning](Pictures%20of%20implementation/Screenshot%202026-09-19%20at%2018.50.02.png)

---

### 🏷️ Automated Label Generation

Scanned products can be selected individually before labels are generated.

The prototype supports two separate label workflows:

1. **Small fold-over jewelry tags**
2. **Larger box/product labels**

![Labels and printing](Pictures%20of%20implementation/Screenshot%202026-09-19%20at%2018.49.53.png)

---

### 📊 Restocking Support

The Restocking interface combines inventory information with sales activity from the previous six months.

For each scanned product, the prototype calculates:

- Current inventory
- Units sold during the previous six months
- Average monthly sales
- Target stock
- Suggested reorder quantity

![Restocking](Pictures%20of%20implementation/Screenshot%202026-09-19%20at%2018.50.11.png)

---

## 💍 Real-World Context

The prototype was designed around an existing jewelry inventory workflow.

Products are stored individually in transparent boxes and accompanied by printed product labels containing identifying information, product imagery, price and a barcode.

![Existing jewelry inventory](Pictures%20of%20implementation/IMG_3240.jpeg)

The goal is therefore not to replace the physical organization of the inventory, but to automate some of the repetitive digital work surrounding it.

---

## 🏷️ Label Workflows

### Small Fold-Over Jewelry Tag

Small jewelry tags are generated as individual PDF pages designed for compact fold-over labels.

The generated tag contains two logical faces:

```text
┌───────────────────────┬────────────────────────┐
│                       │                        │
│      ||||||||||       │       39.00 EUR        │
│       16023451        │  BAGUE PERFECT COUPLE  │
│                       │         ACIER          │
│                       │                        │
└───────────────────────┴────────────────────────┘
       Barcode side              Product side
```

The barcode side contains:

- Code 128 barcode
- Exact 8-digit barcode number

The product side contains:

- Price
- Product name
- Variant/options when available

PDF was selected for this workflow because it provides a convenient previewable and printer-independent output while remaining suitable for printing through a Zebra printer driver.

---

### 📦 A4 Box / Product Labels

Larger labels are generated on a configurable A4 sheet.

Each label can contain:

- Product name
- Variant information
- `STOCK` indicator
- Product image
- Price
- Code 128 barcode
- Human-readable 8-digit barcode

The number of rows and columns can be configured directly from the application.

This allows the same inventory information to be transformed into larger labels suitable for the physical jewelry boxes.

---

## 🔄 Application Workflow

```text
Barcode
   │
   ▼
Validate 8 digits
   │
   ▼
Search product
   │
   ├──────── Demo Mode ────────► Local demo dataset
   │
   └──────── API Mode ─────────► Shopify Admin API
                                      │
                                      ▼
                              Product / Variant
                              Price / Image
                              Inventory
                                      │
                                      ▼
                              Scanned-item list
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             Adjust stock       Generate labels    Restocking
                    │                 │                 │
                    ▼                 ▼                 ▼
             Publish quantity   PDF output       Reorder suggestion
```

---

## 🧪 Demo Mode

The project includes a complete **Demo Mode**, allowing the prototype to be demonstrated without access to a Shopify store.

Demo Mode includes fictional jewelry products with:

- 8-digit barcodes
- Product names
- Variants
- Prices
- Inventory quantities
- Six-month sales values
- Product images

Example demo barcodes include:

```text
10010101
10010102
20014101
30008101
40022001
50033001
60044001
70055001
80066001
90077001
```

Inventory modifications made in Demo Mode are kept in memory for the current application session.

This makes the repository independently testable without exposing or requiring production credentials.

---

## 🛍️ Shopify API Mode

API Mode connects the prototype to Shopify using the **Shopify Admin GraphQL API**.

The barcode is treated as the primary product identifier.

This is intentional: the physical inventory uses **exactly 8 numeric digits**, while SKU values may be empty.

```text
Physical barcode
       │
       ▼
   16023451
       │
       ▼
Shopify variant search
       │
       ▼
Product + variant + inventory
```

The application therefore does not depend on SKU availability.

---

## 📦 Inventory Adjustment

Inventory changes follow a deliberate two-stage process.

Pressing `+` or `−` changes only the **proposed inventory quantity** shown in the interface.

It does **not** immediately modify Shopify.

```text
Current inventory: 2

        −    2    +

             │
             ▼

Proposed inventory: 3

             │
             ▼

      Publish inventory

             │
             ▼

        Shopify API
```

This reduces the risk of accidental inventory writes while scanning or checking physical stock.

In Demo Mode, the same interface updates the in-memory demonstration dataset.

---

## 📈 Restocking Logic

The prototype includes a simple rule-based restocking model.

Average monthly sales are calculated from the previous six months:

```text
Average monthly sales = units sold during 6 months / 6
```

Target stock is then estimated using:

```text
Target stock =
ceil(
    average monthly sales
    × months of coverage
    × safety factor
)
```

Finally:

```text
Recommended order =
max(0, target stock - current inventory)
```

Default parameters:

```text
Months of coverage: 3
Safety factor:      1.20
```

For example:

```text
Sold during 6 months = 18 units

Average monthly sales
= 18 / 6
= 3 units

Target
= ceil(3 × 3 × 1.20)
= 11 units

Current inventory
= 4 units

Recommended order
= 11 - 4
= 7 units
```

This is intentionally a transparent rule-based approach suitable for a prototype.

More sophisticated forecasting could be incorporated in future iterations.

---

## 📁 Repository Structure

```text
jewelry_inventory_phase2/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── services/
│   ├── __init__.py
│   ├── demo_data.py
│   ├── inventory.py
│   ├── labels.py
│   └── shopify.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── app.js
│   ├── style.css
│   └── demo/
│       ├── 10010101.png
│       ├── 10010102.png
│       ├── 20014101.png
│       ├── 30008101.png
│       ├── 40022001.png
│       ├── 50033001.png
│       ├── 60044001.png
│       ├── 70055001.png
│       ├── 80066001.png
│       └── 90077001.png
│
├── generated/
│   └── .gitkeep
│
└── pictures of implementation/
    ├── Screenshot 2026-09-19 at 18.49.53.png
    ├── Screenshot 2026-09-19 at 18.50.02.png
    ├── Screenshot 2026-09-19 at 18.50.11.png
    └── IMG_3240.jpeg
```

---

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Backend | Python |
| Web framework | Flask |
| Frontend | HTML / CSS / JavaScript |
| Commerce platform | Shopify |
| API | Shopify Admin GraphQL API |
| HTTP client | Requests |
| PDF generation | ReportLab |
| Barcode format | Code 128 |
| Configuration | python-dotenv |
| Version control | Git / GitHub |

---

## 🚀 Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/ApteryxDev/Project-Digitalization-and-Automation-Hackathon-DLBCCOEDAH01-.git

cd Project-Digitalization-and-Automation-Hackathon-DLBCCOEDAH01-
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Copy the example configuration:

```bash
cp .env.example .env
```

For Demo Mode, Shopify credentials are not required.

For API Mode, configure the required Shopify values locally in `.env`.

### 5. Start the application

```bash
python app.py
```

The development application is then available at:

```text
http://127.0.0.1:5001
```

---

## 🔐 Security by Design

Sensitive Shopify credentials are loaded through environment variables rather than hard-coded into the source code.

The repository contains:

```text
.env.example
```

but the real:

```text
.env
```

is excluded through `.gitignore`.

The application also keeps API operations server-side so Shopify credentials are never exposed directly to browser JavaScript.

Before publishing or sharing a deployment, any previously exposed API credential should be rotated.

---

## ⚙️ Configuration

The application supports environment-based configuration for values such as:

```text
DATA_MODE
SHOPIFY_SHOP
SHOPIFY_CLIENT_ID
SHOPIFY_CLIENT_SECRET
SHOPIFY_API_VERSION
RESTOCK_MONTHS_COVER
RESTOCK_SAFETY_FACTOR
```

This keeps environment-specific settings separate from application logic.

---

## 📊 Prototype KPIs

The prototype was designed around operational indicators relevant to the original inventory process.

| KPI | What the prototype addresses |
|---|---|
| Item identification time | Barcode lookup replaces manual product searching |
| Tag generation time | Product information is transformed automatically into printable labels |
| Inventory-record error rate | Barcode-based identification reduces manual matching |
| Low-stock detection lag | Restocking logic surfaces stock requirements from inventory and sales data |
| Manual product lookups | Shopify product retrieval is triggered directly from the physical barcode |

The repository does not assume fabricated baseline measurements.

Actual KPI improvement should be evaluated by comparing the prototype against the existing manual workflow under real operating conditions.

---

## 🧠 Design Decisions

### Barcode instead of SKU

The physical inventory already uses an 8-digit barcode system.

Shopify SKU fields may be empty, so the barcode is used as the authoritative identifier throughout the prototype.

### PDF instead of printer-specific output

The small jewelry tags are generated as PDF files rather than requiring direct printer-language output.

This provides:

- Browser preview
- Easy downloading
- Printer independence
- Compatibility with a Zebra printer through its normal print driver
- Easier testing during prototype development

### Explicit inventory publishing

Inventory is not updated every time `+` or `−` is pressed.

The operator must explicitly publish the proposed quantity.

This separates **counting** from **committing an inventory change**.

### Demo and API modes

The same interface supports both fictional demonstration data and real Shopify information.

This allows the prototype to remain reproducible while still demonstrating integration with an operational commerce platform.

---

## 🚧 Limitations

This repository represents a **proof of concept**, not a production inventory-management system.

Current limitations include:

- Restocking uses a simple historical-sales formula rather than demand forecasting
- Demo inventory is stored in memory
- The Flask development server is intended for local demonstration
- Printer calibration can vary depending on the physical label stock and Zebra model
- Shopify inventory behavior can depend on store locations and API permissions
- Supplier ordering is not automated

---

## 🔮 Future Improvements

Possible extensions include:

- Time-series demand forecasting
- Seasonal sales modelling
- Supplier API integration
- Automatic purchase-order generation
- Supplier email automation
- Multi-location inventory management
- Persistent local database for offline workflows
- Authentication and user roles
- Scan-history analytics
- Inventory discrepancy reports
- Automatic low-stock notifications
- Mobile barcode-scanner interface
- Dedicated Zebra printer calibration profiles

A future version could replace the current rule-based restocking calculation with a forecasting model trained on historical product demand.

---

## 🎓 Project Context

This prototype was developed for:

**Project: Digitalization and Automation Hackathon**  
**Course:** `DLBCCOEDAH01`  
**Programme:** Bachelor of Applied Artificial Intelligence  
**Institution:** IU International University

The project demonstrates the transition from an existing manual business workflow toward a partially automated digital process.

The implementation combines:

- Process digitalization
- API integration
- Inventory automation
- Barcode-based identification
- Automated document generation
- Basic decision-support logic
- Human-controlled inventory updates

---

## 👤 Author

**Alp Ege Yalcin**  
Applied Artificial Intelligence  
IU International University

GitHub: **[@ApteryxDev](https://github.com/ApteryxDev)**

---

## 📄 License

This repository was created as an academic prototype for the IU **Digitalization and Automation Hackathon**.

Product and store data used through API Mode belong to their respective owners. Demo data is included solely for demonstration and testing purposes.
