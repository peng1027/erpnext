# CLAUDE.md

This file provides guidance to Claude Code when working with the ERPNext codebase.

## Overview

ERPNext is an open-source ERP system built on the **Frappe Framework**. It provides modules for accounting, inventory, manufacturing, CRM, HR, and more. ERPNext is a Frappe app that runs within a bench environment.

## Commands

```bash
# Development server
bench start

# Run all tests
bench --site <site> run-tests --app erpnext

# Run module tests
bench --site <site> run-tests --module erpnext.accounts

# Run specific test file
bench --site <site> run-tests --module erpnext.accounts.doctype.sales_invoice.test_sales_invoice

# Run single test method
bench --site <site> run-tests --module erpnext.accounts.doctype.sales_invoice.test_sales_invoice --test test_sales_invoice_creation

# Console, migrations, cache
bench --site <site> console
bench --site <site> migrate
bench --site <site> clear-cache
bench build --app erpnext
```

### Linting

```bash
pre-commit run --all-files   # ruff + prettier + eslint
ruff check erpnext/          # Python lint
ruff format erpnext/         # Python format
```

Config: `pyproject.toml` (line-length=110, tab indentation), `.eslintrc`, `.pre-commit-config.yaml`

## Architecture

### Directory Structure

```
erpnext/
├── accounts/              # Accounting (GL, invoices, payments, taxes)
├── assets/                # Fixed asset management
├── bulk_transaction/      # Bulk transaction processing
├── buying/                # Purchasing (purchase orders, suppliers)
├── communication/         # Communication tracking
├── controllers/           # Shared business logic controllers
├── crm/                   # Customer relationship management
├── edi/                   # Electronic data interchange
├── erpnext_integrations/  # Third-party integrations
├── maintenance/           # Maintenance schedules
├── manufacturing/         # Production (BOM, work orders, job cards)
├── patches/               # Database migration patches
├── projects/              # Project management and timesheets
├── quality_management/    # Quality inspection and procedures
├── regional/              # Country-specific tax/compliance
├── selling/               # Sales (quotations, sales orders)
├── setup/                 # Installation and setup wizard
├── shopping_cart/         # E-commerce cart
├── stock/                 # Inventory (items, warehouses, stock entries)
├── subcontracting/        # Subcontracting workflows
├── support/               # Issue tracking and SLA
├── telephony/             # Call integration
├── utilities/             # Shared utility functions
├── www/                   # Web pages and portals
└── hooks.py               # Frappe app hooks configuration
```

### DocType Pattern

Each business entity (Invoice, Item, Customer) is a DocType with:
- `<doctype>.json` — Field definitions and configuration
- `<doctype>.py` — Server-side logic (validation, calculations)
- `<doctype>.js` — Client-side UI interactions
- `test_<doctype>.py` — Unit tests
- `test_records.json` — Test data fixtures

### Controllers

Shared logic in `erpnext/controllers/`:
- `accounts_controller.py` — Base for accounting documents
- `buying_controller.py` — Purchase document logic
- `selling_controller.py` — Sales document logic
- `stock_controller.py` — Inventory transaction logic
- `taxes_and_totals.py` — Tax calculations shared across transactions

**Inheritance chain**:
```
TransactionBase → AccountsController → BuyingController → PurchaseOrder
                                     → SellingController → SalesInvoice
```

### Key Concepts

- **Company**: Multi-company support; most transactions are company-scoped
- **Cost Center**: Departmental accounting/budgeting
- **Warehouse**: Hierarchical inventory locations
- **Item**: Products/services with variants, pricing, stock tracking
- **Stock Ledger Entry (SLE)**: Immutable stock movement records
- **General Ledger Entry (GLE)**: Immutable accounting entries

### Frappe APIs Used Frequently

- `frappe.get_doc()` — Load documents
- `frappe.db.get_value()` / `frappe.db.set_value()` — Database operations
- `@frappe.whitelist()` — Expose methods as API endpoints
- `frappe.throw()` / `frappe.msgprint()` — User messages

## Testing

```python
class TestSalesInvoice(FrappeTestCase):
    def test_sales_invoice_creation(self):
        si = create_sales_invoice()
        self.assertEqual(si.docstatus, 1)
```

## Dependencies

- **Frappe Framework**: Version managed by bench environment (see `pyproject.toml`)
- **Python**: 3.10+
- **MariaDB**: 10.6+
- **Redis**: Caching and background jobs
- **Node.js**: Frontend asset building
