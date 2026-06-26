# Employee Loan Task - Odoo 17 Module

A comprehensive employee loan management system for Odoo 17 that enables HR departments to create, approve, track, and manage employee loans with automated payment schedules and accounting integration.

## Overview

This module provides a complete solution for managing employee loans, from loan request creation through payment tracking and reporting. It includes workflow management, installment scheduling, accounting journal entries, and comprehensive reporting capabilities.

## Features

### Core Loan Management
- **Loan Creation & Tracking**: Create loans linked to employee records with automatic workflow states
- **Loan States**: Draft → Pending → Approved/Rejected → Paid
- **Employee Information**: Auto-populated department and job position data
- **Loan Details**: Track loan amount, start date, number of installments, and payment schedule

### Payment & Installments
- **Automatic Installment Generation**: Generates monthly installment lines based on loan amount and number of installments
- **Installment Tracking**: Monitor due dates, amounts, and payment status
- **Payment Schedule**: Visual representation of all scheduled payments

### Accounting Integration
- **Journal Entry Creation**: Automatically creates accounting entries when loan is approved
- **Multi-Account Support**: Links to employee loan accounts and payment journals
- **Double-Entry Bookkeeping**: Properly debits employee account and credits payment account

### Workflow & Approval
- **State Management**: Complete workflow from draft through paid status
- **Approval Process**: Managers can approve or reject loans with reasons
- **Audit Trail**: Changes tracked with mail.thread and mail.activity.mixin

### Reporting & Wizards
- **PDF Reports**: Generate loan reports from form or list views
- **Loan Wizard**: Transient model for creating loans with simplified interface
- **Loan Summary Wizard**: View outstanding loan balances and payment schedules

### Security & Access Control
- **Role-Based Access**: Separate access levels for different user groups
- **Record Rules**: Security rules defined in `security.xml`
- **Manager-Only Fields**: Sensitive fields restricted to loan managers

## Installation

1. Copy this module folder to your Odoo `addons` directory:
   ```
   cp -r employee_loan_task /path/to/odoo/addons/
   ```

2. Restart Odoo service:
   ```
   sudo systemctl restart odoo
   ```

3. Update the app list in Odoo:
   - Go to **Apps** → Click **Update Apps List**

4. Install the module:
   - Search for "Employee Loan"
   - Click **Install**

## Configuration

### Prerequisites
- Ensure employee records exist in the HR module
- Create at least one accounting journal for loan payments
- Configure employee loan accounts in the chart of accounts

### Setup Steps
1. Navigate to **Employees** → Select an employee → Configure:
   - Loan Account (linked to accounting)
   - Any other employee-specific settings

2. Set up **Journals** for loan payments:
   - Go to **Accounting** → **Journals**
   - Create a new journal or use an existing one for loan disbursements

3. Adjust access rights if needed:
   - Edit `security/ir.model.access.csv` to customize user permissions
   - Define additional security rules in `security/security.xml`

## Usage

### Creating a Loan

1. Go to **Employees** → **Employee Loans**
2. Click **Create** to open a new loan form
3. Fill in:
   - **Employee**: Select the employee
   - **Loan Amount**: Total amount to lend
   - **Start Date**: Loan disbursement date
   - **Number of Installments**: Monthly payment count
   - **Payment Journal**: Select the accounting journal
4. Click **Save**
5. Click **Send for Approval** (if workflow enabled)

### Approving a Loan

1. Open the loan record
2. Review the details and installment schedule
3. Click **Approve** to:
   - Create accounting journal entries automatically
   - Generate monthly installment lines
   - Update loan state to "Approved"
4. Click **Reject** if the loan should be declined (option to add rejection reason)

### Tracking Payments

1. Open the loan to view the **Installment Lines** tab
2. Each line shows:
   - Installment number
   - Due date
   - Amount
   - Payment status

### Generating Reports

1. Open a loan record or list view
2. Click the **Print** menu
3. Select **Employee Loan Report** to generate PDF

### Using Wizards

- **Employee Loan Wizard**: Simplified interface for quick loan creation
- **Loan Summary Wizard**: View all outstanding loans and their payment schedules

## Module Structure

```
employee_loan_task/
├── __manifest__.py              # Module metadata
├── __init__.py                  # Package initialization
├── README.md                    # This file
│
├── models/
│   ├── __init__.py
│   ├── employee_loan.py         # Main Employee Loan model
│   └── hr_employee.py           # Extended HR Employee fields
│
├── views/
│   ├── base_menu.xml            # Menu structure
│   ├── employee_loan.xml        # Loan form and list views
│   └── hr_employee.xml          # Extended employee views
│
├── wizard/
│   ├── __init__.py
│   ├── employee_loan_wizard.py  # Loan creation wizard (transient)
│   ├── employee_loan_wizard.xml # Wizard view
│   ├── loan_summary_wizard.py   # Loan summary wizard (transient)
│   └── loan_summary_wizard_view.xml # Summary wizard view
│
├── reports/
│   └── employee_loan_report.xml # QWeb report template
│
├── security/
│   ├── ir.model.access.csv      # Object-level access control
│   └── security.xml             # Record rules and groups
│
└── static/
    └── src/
        └── css/
            ├── employee_loan.css # Loan form styling
            └── loan_lines.css    # Installment lines styling
```

## Key Models

### employee.loan
Main model for loan records with fields:
- **Employee Details**: employee_id, department_id, job_id
- **Loan Details**: loan_amount, start_at, installments_nums, monthly_installment
- **Workflow**: state, reject_reason
- **Accounting**: journal_id, loan_account_id, move_id
- **Relations**: line_ids (One2many to loan.lines)

### loan.lines
Child model representing individual installment payments:
- installment_date
- amount
- installments_num
- state (due, paid, etc.)

## Dependencies

- `base`: Core Odoo functionality
- `account`: Accounting and journal entries
- `hr`: Human resources and employee data
- `mail`: Message threading and activity tracking

## Workflow States

| State | Description |
|-------|-------------|
| **Draft** | Initial state, loan not yet submitted |
| **Pending** | Waiting for manager approval |
| **Approved** | Loan approved, journal entries created, installments generated |
| **Rejected** | Loan rejected with reason recorded |
| **Paid** | All installments paid |

## Security Groups

- **Employee Loan Manager**: Full access to create, approve, and manage all loans
- **Employee**: Can view own loan records
- Additional groups defined in `security.xml`

## Development & Customization

### Adding Custom Fields

1. Edit `models/employee_loan.py` to add new fields
2. Create an XML view in `views/employee_loan.xml`
3. Update `security/ir.model.access.csv` if needed

### Extending the Report

1. Modify `reports/employee_loan_report.xml`
2. Add QWeb elements or use computation methods

### Styling

- Modify `static/src/css/employee_loan.css` for form styling
- Modify `static/src/css/loan_lines.css` for installment lines

### Testing

1. Restart Odoo after making changes
2. Update the module from **Apps** menu
3. Use Odoo logs to debug:
   ```
   sudo tail -f /var/log/odoo/odoo-server.log
   ```

## Troubleshooting

### Loan won't approve
- Check that **Payment Journal** is configured
- Verify **Loan Account** is set on the employee
- Ensure loan amount > 0

### Missing installment lines
- Verify the number of installments is set correctly
- Check that start date is valid
- Restart Odoo and try again

### Accounting entries not created
- Ensure the journal has a default account configured
- Check user permissions for the accounting module
- Verify both loan account and journal account are configured

## Author

Ahmed

## License

LGPL-3

Contributing
------------

Open a PR with clear description and test steps. Keep code style consistent with Odoo conventions.

License
-------
Specify your license here (e.g., AGPL-3, LGPL, MIT). If none is provided, add one to the module manifest.

Files of interest
- `models/employee_loan.py` — main loan model and logic.
- `views/employee_loan.xml` — loan form and tree views.
- `wizard/loan_summary_wizard.py` — loan summary logic and view.

Contact
-------
Module author or maintainer information (add your name/email here).
