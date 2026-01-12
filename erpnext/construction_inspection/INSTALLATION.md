# Construction Inspection Module - Installation Guide

This guide provides step-by-step instructions for installing and configuring the Construction Inspection module in ERPNext.

## Prerequisites

### System Requirements
- **ERPNext Version**: 13.0 or higher
- **Python**: 3.6 or higher
- **Database**: MariaDB 10.3+ or MySQL 8.0+
- **Node.js**: 14.0 or higher (for frontend assets)
- **Redis**: For caching and background jobs

### Required ERPNext Modules
The following ERPNext modules must be installed and configured:
- Core (always installed)
- Buying (for supplier management)
- Projects (for project integration)
- Setup (for custom fields and workflows)

## Installation Steps

### Step 1: Backup Your System

Before installing any new module, create a complete backup:

```bash
# Create database backup
bench --site [site-name] backup --with-files

# Verify backup location
ls -la sites/[site-name]/private/backups/
```

### Step 2: Download the Module

Since this is a custom module integrated into ERPNext, the files should be placed in the appropriate directory structure:

```bash
# Navigate to your ERPNext app directory
cd apps/erpnext/erpnext/

# Verify the construction_inspection directory exists
ls -la construction_inspection/
```

### Step 3: Install Dependencies

Install any additional Python dependencies:

```bash
# Navigate to your bench directory
cd /path/to/your/bench

# Install dependencies (if any additional packages are required)
pip install -r apps/erpnext/requirements.txt
```

### Step 4: Database Migration

Run database migrations to create the required tables and fields:

```bash
# Run migrations for the site
bench --site [site-name] migrate

# Clear cache
bench --site [site-name] clear-cache

# Rebuild search index
bench --site [site-name] build-search-index
```

### Step 5: Install Fixtures

Install the module's fixtures (custom fields, workflows, etc.):

```bash
# Install fixtures
bench --site [site-name] install-fixtures

# Or manually install specific fixtures
bench --site [site-name] execute erpnext.construction_inspection.setup.install.install_fixtures
```

### Step 6: Restart Services

Restart all bench services:

```bash
# Restart bench
bench restart

# Or restart individual services
sudo supervisorctl restart all
```

## Post-Installation Configuration

### Step 1: Verify Installation

1. **Login to ERPNext**
   - Access your ERPNext instance
   - Login with System Manager credentials

2. **Check Module Availability**
   - Go to `Modules` page
   - Verify "Construction Inspection" module is visible
   - Click on the module to access its features

3. **Verify DocTypes**
   - Go to `Setup > Customize > DocType`
   - Search for "Construction Site" and "Supplier Inspection"
   - Verify both DocTypes exist and are accessible

### Step 2: Configure User Roles

1. **Create/Assign Roles**
   ```bash
   # Access Role Manager
   Setup > Users and Permissions > Role Manager
   ```

2. **Configure Role Permissions**
   - **Construction Manager**: Full access to all construction inspection features
   - **Quality Inspector**: Create and manage inspections
   - **Site Supervisor**: Site-specific access
   - **Supplier**: Limited access to assigned sites

3. **Assign Users to Roles**
   ```bash
   # Go to User List
   Setup > Users and Permissions > User
   
   # Edit each user and assign appropriate roles
   ```

### Step 3: Set Up Custom Fields

The module automatically creates custom fields. Verify they exist:

1. **Supplier Custom Fields**
   - Go to `Buying > Supplier > [Any Supplier]`
   - Check for inspection-related fields in the form

2. **Project Custom Fields**
   - Go to `Projects > Project > [Any Project]`
   - Verify construction site linkage fields

### Step 4: Configure Workflows

1. **Verify Workflow Installation**
   ```bash
   Setup > Workflow > Workflow
   ```
   - Look for "Supplier Inspection Workflow"

2. **Customize Workflow (Optional)**
   - Modify states and transitions as needed
   - Assign appropriate roles to workflow actions

### Step 5: Set Up Notifications

1. **Configure Email Settings**
   ```bash
   Setup > Email > Email Account
   ```
   - Ensure SMTP settings are configured
   - Test email sending functionality

2. **Verify Notification Rules**
   ```bash
   Setup > Notifications > Notification
   ```
   - Check for construction inspection notifications
   - Customize recipients and conditions as needed

### Step 6: Initialize Sample Data (Optional)

For testing and demonstration purposes:

```python
# Execute in ERPNext console
bench --site [site-name] console

# In the console:
from erpnext.construction_inspection.test_data.sample_data import create_sample_data
create_sample_data()
```

## Configuration Settings

### Module Settings

1. **Access Construction Inspection Settings**
   ```bash
   Construction Inspection > Settings > Construction Inspection Settings
   ```

2. **Configure Default Values**
   - Default inspection interval (days)
   - Rating scale (1-5 or 1-10)
   - Automatic approval thresholds
   - Notification preferences

### Dashboard Configuration

1. **Enable Dashboard**
   - Go to `Workspace > Construction Inspection`
   - Verify dashboard widgets are visible
   - Customize dashboard layout as needed

2. **Configure Charts**
   - Inspection Rating Trend
   - Supplier Performance
   - Inspection Status Distribution

## Testing Installation

### Step 1: Create Test Data

1. **Create Test Supplier**
   ```bash
   Buying > Supplier > New
   ```
   - Name: "Test Construction Supplier"
   - Group: "Construction"

2. **Create Test Construction Site**
   ```bash
   Construction Inspection > Construction Site > New
   ```
   - Site Name: "Test Site 1"
   - Site Code: "TS-001"
   - Supplier: Select the test supplier

3. **Create Test Inspection**
   ```bash
   Construction Inspection > Supplier Inspection > New
   ```
   - Select the test site and supplier
   - Add checklist items
   - Submit for approval

### Step 2: Test Workflows

1. **Test Approval Process**
   - Create an inspection
   - Submit for approval
   - Verify workflow transitions

2. **Test Notifications**
   - Check notification logs
   - Verify email notifications (if configured)

### Step 3: Test Integrations

1. **Project Integration**
   - Create a project with "construction" in the name
   - Verify automatic site creation

2. **Supplier Integration**
   - Check supplier performance metrics
   - Verify custom fields are populated

## Troubleshooting

### Common Installation Issues

1. **Migration Errors**
   ```bash
   # Check migration logs
   tail -f logs/worker.error.log
   
   # Retry migration
   bench --site [site-name] migrate --skip-failing
   ```

2. **Permission Errors**
   ```bash
   # Reset permissions
   bench --site [site-name] execute frappe.permissions.reset_perms
   
   # Rebuild permissions
   bench --site [site-name] execute erpnext.construction_inspection.setup.install.setup_permissions
   ```

3. **Custom Field Issues**
   ```bash
   # Reinstall custom fields
   bench --site [site-name] execute erpnext.construction_inspection.setup.install.install_custom_fields
   ```

4. **Workflow Problems**
   ```bash
   # Reinstall workflows
   bench --site [site-name] execute erpnext.construction_inspection.setup.install.install_workflows
   ```

### Performance Optimization

1. **Database Indexing**
   ```sql
   -- Add indexes for better performance
   ALTER TABLE `tabSupplier Inspection` ADD INDEX `idx_site_date` (`construction_site`, `inspection_date`);
   ALTER TABLE `tabConstruction Site` ADD INDEX `idx_supplier_status` (`supplier`, `status`);
   ```

2. **Cache Configuration**
   ```bash
   # Increase cache size if needed
   bench config set cache_size 1000
   bench restart
   ```

### Monitoring and Maintenance

1. **Log Monitoring**
   ```bash
   # Monitor error logs
   tail -f logs/web.error.log
   tail -f logs/worker.error.log
   
   # Check scheduled job logs
   tail -f logs/schedule.log
   ```

2. **Database Maintenance**
   ```bash
   # Regular database optimization
   bench --site [site-name] execute frappe.db.sql("OPTIMIZE TABLE `tabSupplier Inspection`")
   bench --site [site-name] execute frappe.db.sql("OPTIMIZE TABLE `tabConstruction Site`")
   ```

## Uninstallation (If Needed)

### Step 1: Backup Data

```bash
# Export construction inspection data
bench --site [site-name] export-doc "Construction Site"
bench --site [site-name] export-doc "Supplier Inspection"
```

### Step 2: Remove Custom Fields

```python
# Execute in ERPNext console
from erpnext.construction_inspection.setup.uninstall import remove_custom_fields
remove_custom_fields()
```

### Step 3: Remove Workflows

```python
# Execute in ERPNext console
from erpnext.construction_inspection.setup.uninstall import remove_workflows
remove_workflows()
```

### Step 4: Clean Database

```bash
# Remove module data (CAUTION: This will delete all data)
bench --site [site-name] execute erpnext.construction_inspection.setup.uninstall.cleanup_module_data
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly Tasks**
   - Review error logs
   - Check notification delivery
   - Monitor system performance

2. **Monthly Tasks**
   - Database optimization
   - Archive old inspection data
   - Review and update configurations

3. **Quarterly Tasks**
   - Full system backup
   - Performance analysis
   - User training updates

### Getting Help

1. **Documentation**
   - Module README.md
   - ERPNext Documentation
   - Frappe Framework Docs

2. **Community Support**
   - ERPNext Forum
   - GitHub Issues
   - Community Chat

3. **Professional Support**
   - Frappe Technologies
   - Certified ERPNext Partners
   - Custom Development Services

---

**Note**: Always test the installation in a development environment before deploying to production. Keep regular backups and monitor system performance after installation.