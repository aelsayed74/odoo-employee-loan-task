{
    'name': "Employee Loan",
    'version': '1.0',
    'license': 'LGPL-3',
    # depends takes tech names which appear with red line when you activate debug mood 
    'depends': ['base','account','hr','mail'],
    'author': "Ahmed",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': ["security/security.xml",
             "security/ir.model.access.csv",
             "views/base_menu.xml",
             "views/employee_loan.xml",
             "views/hr_employee.xml",
             "wizard/employee_loan_wizard.xml",
             "wizard/loan_summary_wizard_view.xml",
             "reports/employee_loan_report.xml",
             ],
    'assets': {
    'web.assets_backend': [
        'employee_loan_task/static/src/css/loan_lines.css',
        'employee_loan_task/static/src/css/employee_loan.css',
    ],},
    # data files containing optionally loaded demonstration data
    'installable': True,
    'application': True,
}