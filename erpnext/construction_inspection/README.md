# Construction Inspection Module for ERPNext

A comprehensive construction inspection management module for ERPNext that enables systematic tracking, evaluation, and reporting of construction site inspections and supplier performance.

## Features

### Core Functionality
- **Construction Site Management**: Track multiple construction sites with detailed information
- **Supplier Inspection**: Comprehensive inspection system with customizable checklists
- **Quality Control**: Rating system and approval workflows
- **Progress Tracking**: Automated progress calculation and reporting
- **Issue Management**: Track and manage inspection issues and corrective actions

### Integration Capabilities
- **Project Management**: Seamless integration with ERPNext Project module
- **Supplier Management**: Enhanced supplier performance tracking
- **User Permissions**: Role-based access control and site assignments
- **Notification System**: Automated alerts and reminders
- **Reporting**: Comprehensive analytics and dashboard

### Automation Features
- **Scheduled Tasks**: Daily reminders, weekly reports, monthly analytics
- **Workflow Management**: Automated approval processes
- **Data Synchronization**: Real-time updates across modules
- **Performance Metrics**: Automatic calculation of KPIs

## Installation

### Prerequisites
- ERPNext v13.0 or higher
- Python 3.6+
- MariaDB/MySQL database

### Installation Steps

1. **Navigate to your ERPNext bench directory:**
   ```bash
   cd /path/to/your/bench
   ```

2. **Install the module:**
   ```bash
   bench get-app construction_inspection
   bench --site your-site-name install-app construction_inspection
   ```

3. **Run database migrations:**
   ```bash
   bench --site your-site-name migrate
   ```

4. **Clear cache and restart:**
   ```bash
   bench --site your-site-name clear-cache
   bench restart
   ```

## Configuration

### Initial Setup

1. **Access Module Settings:**
   - Go to `Setup > Construction Inspection > Construction Inspection Settings`
   - Configure default inspection intervals, rating scales, and notification preferences

2. **Set up User Roles:**
   - Assign users to appropriate roles:
     - `Construction Manager`: Full access to all features
     - `Quality Inspector`: Create and manage inspections
     - `Site Supervisor`: Site-specific access
     - `Supplier`: Limited access to assigned sites

3. **Configure Workflows:**
   - The module includes pre-configured workflows for inspection approval
   - Customize workflow states and transitions as needed

### Custom Fields Setup

The module automatically adds custom fields to existing DocTypes:

- **Supplier**: Inspection metrics and performance ratings
- **Project**: Construction site linkage
- **User**: Site assignments and permissions

### Notification Configuration

1. **Email Settings:**
   - Configure SMTP settings in ERPNext
   - Set up email templates for notifications

2. **Notification Rules:**
   - Daily inspection reminders
   - Approval/rejection notifications
   - Progress update alerts

## Usage Guide

### Creating Construction Sites

1. Navigate to `Construction Inspection > Construction Site`
2. Click "New" to create a new site
3. Fill in required information:
   - Site Name and Code
   - Supplier assignment
   - Location details
   - Expected dates

### Conducting Inspections

1. Go to `Construction Inspection > Supplier Inspection`
2. Create new inspection:
   - Select construction site and supplier
   - Choose inspection type (Routine, Special, Final)
   - Add checklist items with ratings
   - Include photos and comments

3. Submit for approval:
   - Review overall rating calculation
   - Submit to workflow for approval
   - Track approval status

### Managing Checklists

1. Create inspection templates:
   - Go to `Construction Inspection > Inspection Checklist Item`
   - Define standard checklist items
   - Set weights and mandatory flags

2. Use templates in inspections:
   - Select from predefined templates
   - Customize for specific inspections
   - Add site-specific items

### Monitoring Performance

1. **Dashboard Access:**
   - View real-time metrics on the Construction Inspection dashboard
   - Monitor inspection trends and supplier performance

2. **Reports:**
   - `Inspection Summary`: Overview of all inspections
   - `Site Progress Report`: Detailed site progress tracking
   - `Supplier Performance Report`: Comprehensive supplier analytics

## API Reference

### Key DocTypes

#### Construction Site
```python
# Create a new construction site
site = frappe.get_doc({
    "doctype": "Construction Site",
    "site_name": "Project Alpha Site 1",
    "site_code": "PA-001",
    "supplier": "ABC Construction Ltd",
    "status": "Active"
})
site.insert()
```

#### Supplier Inspection
```python
# Create a new inspection
inspection = frappe.get_doc({
    "doctype": "Supplier Inspection",
    "construction_site": "PA-001",
    "supplier": "ABC Construction Ltd",
    "inspection_date": "2024-01-15",
    "inspector": "john.doe@company.com",
    "inspection_type": "Routine"
})
inspection.insert()
```

### Integration Functions

#### Project Integration
```python
from erpnext.construction_inspection.integrations.project_integration import (
    sync_project_construction_sites,
    get_project_construction_sites
)

# Sync projects with construction sites
sync_project_construction_sites()

# Get sites for a specific project
sites = get_project_construction_sites("PROJECT-001")
```

#### Supplier Integration
```python
from erpnext.construction_inspection.integrations.supplier_integration import (
    get_supplier_inspection_analytics,
    update_supplier_performance_rating
)

# Get supplier analytics
analytics = get_supplier_inspection_analytics("SUPPLIER-001")

# Update performance rating
update_supplier_performance_rating("SUPPLIER-001")
```

### Scheduled Tasks

The module includes automated tasks:

- **Daily**: Inspection reminders and progress updates
- **Weekly**: Site progress reports
- **Monthly**: Performance analytics and data archival

## Customization

### Adding Custom Fields

```python
# Add custom field to Construction Site
custom_field = frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Construction Site",
    "fieldname": "custom_field_name",
    "label": "Custom Field Label",
    "fieldtype": "Data"
})
custom_field.insert()
```

### Custom Workflows

1. Create custom workflow states
2. Define transitions and conditions
3. Assign to Supplier Inspection DocType

### Custom Reports

Create custom reports using ERPNext's Report Builder or Script Reports for specific analytics needs.

## Testing

### Running Tests

```bash
# Run all construction inspection tests
bench --site your-site-name run-tests erpnext.construction_inspection

# Run specific test files
bench --site your-site-name run-tests erpnext.construction_inspection.tests.test_construction_site
bench --site your-site-name run-tests erpnext.construction_inspection.tests.test_supplier_inspection
```

### Test Data Setup

```python
# Create sample data for testing
from erpnext.construction_inspection.test_data.sample_data import create_sample_data

create_sample_data()
```

## Troubleshooting

### Common Issues

1. **Permission Errors:**
   - Ensure users have appropriate roles assigned
   - Check User Permission records for site access

2. **Workflow Issues:**
   - Verify workflow states and transitions
   - Check user permissions for workflow actions

3. **Integration Problems:**
   - Ensure all required modules are installed
   - Check custom field creation

4. **Notification Failures:**
   - Verify email settings configuration
   - Check notification log for error details

### Debug Mode

Enable developer mode for detailed error logging:
```bash
bench --site your-site-name set-config developer_mode 1
bench restart
```

### Log Files

Check log files for detailed error information:
- `logs/web.error.log`
- `logs/worker.error.log`
- `logs/schedule.log`

## Support

### Documentation
- ERPNext Documentation: https://docs.erpnext.com
- Frappe Framework: https://frappeframework.com/docs

### Community
- ERPNext Forum: https://discuss.erpnext.com
- GitHub Issues: Report bugs and feature requests

### Professional Support
Contact Frappe Technologies for professional support and customization services.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This module is licensed under the MIT License. See LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- Core inspection functionality
- Project and supplier integration
- Automated workflows and notifications
- Comprehensive reporting system

---

For more information and updates, visit the [Construction Inspection Module Documentation](https://github.com/your-repo/construction-inspection).