# Excel Import Feature - Quick Guide

## Overview
Added Excel bulk import functionality for medications and batches through popup modals in the Pharmacy Inventory Dashboard.

## Features

### ✅ Import Medications Modal
- **Access**: Click "Import Medications" button on inventory dashboard
- **Modal ID**: `importMedicationsModal`
- **Required Columns**:
  - `name` - Medication name
  - `generic_name` - Generic name
  - `category` - Category (e.g., Antibiotics)
  - `dosage_form` - Form (e.g., Tablet, Capsule)
  - `strength` - Strength (e.g., 500mg)
  - `unit_of_measure` - Unit (e.g., tablets)
- **Features**:
  - Download template with sample data
  - Skip duplicate entries option
  - Progress indicator during import
  - Detailed results display

### ✅ Import Batches Modal
- **Access**: Click "Import Batches" button on inventory dashboard
- **Modal ID**: `importBatchesModal`
- **Required Columns**:
  - `medication_name` - Medication name (must exist in system)
  - `batch_number` - Unique batch number
  - `quantity` - Initial quantity
  - `manufacturing_date` - Format: YYYY-MM-DD
  - `expiry_date` - Format: YYYY-MM-DD
  - `cost_price` - Cost per unit
  - `selling_price` - Selling price per unit
- **Features**:
  - Download template with sample data
  - Skip duplicate batch numbers option
  - Progress indicator during import
  - Detailed results display

## Files Created

1. **`pharmacy/excel_views.py`** (310 lines)
   - `import_medications()` - Handle medication Excel import
   - `import_batches()` - Handle batch Excel import
   - `download_medication_template()` - Generate medication template
   - `download_batch_template()` - Generate batch template

2. **Excel Import Modals** in `pharmacy/templates/pharmacy/modals/all_pharmacy_modals.html`
   - Import Medications Modal (lines 858-919)
   - Import Batches Modal (lines 921-983)
   - JavaScript handlers (lines 985-1129)

## Files Modified

1. **`pharmacy/templates/pharmacy/inventory_dashboard.html`**
   - Added "Import Medications" button (line 18-20)
   - Added "Import Batches" button (line 21-23)

2. **`pharmacy/urls.py`**
   - Imported excel_views (lines 6-9)
   - Added 4 new URL patterns (lines 72-75)

## Usage Instructions

### Import Medications:

1. **Navigate** to Pharmacy Inventory Dashboard
2. **Click** "Import Medications" button (blue button in header)
3. **Download** template by clicking "Download Template"
4. **Fill** Excel file with your medication data
5. **Upload** completed file in modal
6. **Select** "Skip duplicate entries" (recommended)
7. **Click** "Import" button
8. **Review** import results

### Import Batches:

1. **Navigate** to Pharmacy Inventory Dashboard
2. **Click** "Import Batches" button (yellow button in header)
3. **Download** template by clicking "Download Template"
4. **Fill** Excel file with batch data
   - Ensure medication names match exactly
   - Use YYYY-MM-DD format for dates
5. **Upload** completed file in modal
6. **Select** "Skip duplicate batch numbers" (recommended)
7. **Click** "Import" button
8. **Review** import results

## Template Files

### Medication Template
- **File**: `medication_import_template.xlsx`
- **Header Color**: Blue (#1B5E96)
- **Sample Rows**: 3 example medications
- **Columns**: 6 required fields

### Batch Template
- **File**: `batch_import_template.xlsx`
- **Header Color**: Green (#2E8B57)
- **Sample Rows**: 3 example batches
- **Columns**: 7 required fields

## Technical Details

### Dependencies
```bash
pip install openpyxl
```

### URL Routes
| Function | URL | Method |
|----------|-----|--------|
| Import Medications | `/pharmacy/import/medications/` | POST |
| Import Batches | `/pharmacy/import/batches/` | POST |
| Medication Template | `/pharmacy/templates/medications/` | GET |
| Batch Template | `/pharmacy/templates/batches/` | GET |

### Features
- ✅ Modal-based interface (no page navigation)
- ✅ Template download with sample data
- ✅ Duplicate detection
- ✅ Progress indicator
- ✅ Detailed results
- ✅ Transaction safety (rollback on errors)
- ✅ Auto page reload on success

## Error Handling

### Common Errors:

**"Missing columns"**
- Download fresh template
- Ensure all required columns present

**"Medication not found"** (Batches)
- Import medications first
- Check medication name spelling

**"Error reading file"**
- Ensure file is .xlsx or .xls
- File size under 10MB

## Benefits

- ⏱️ **Time Savings**: Import 100+ items in minutes
- ✓ **Data Quality**: Template validation
- 📊 **Visibility**: Clear success/error reporting
- 🔒 **Safety**: Transaction rollback on errors
- 🚀 **Efficiency**: No page reloads needed

## Installation

1. **Install dependency**:
   ```bash
   pip install openpyxl
   ```

2. **Restart server**:
   ```bash
   python manage.py runserver
   ```

3. **Access dashboard**:
   Navigate to: `/pharmacy/inventory/dashboard/`

4. **Test import**:
   - Click "Import Medications" or "Import Batches"
   - Download template
   - Import sample data

## Status

✅ **Complete and Ready**
- Modals integrated
- Backend views created
- URLs configured
- Templates included
- Error handling implemented

---

**Last Updated**: November 12, 2025  
**Version**: 1.0
