# Contributing to Employee Loan Task

Thank you for your interest in contributing to the Employee Loan Task module for Odoo 17.

## Getting Started

1. Fork the repository and clone your fork.
2. Install and configure an Odoo 17 development environment.
3. Copy this module into the `addons` path used by your Odoo instance.
4. Restart Odoo and update the app list.
5. Install the `employee_loan_task` module in your database.

## Coding Guidelines

- Follow Odoo best practices for module development.
- Keep business logic in Python models and wizards under `models/` and `wizard/`.
- Define XML views and menu items clearly under `views/`.
- Keep report templates in `reports/` and security rules in `security/`.
- Use meaningful field names, help text, and comments where needed.
- Keep translations and labels consistent with Odoo conventions.

## Testing

- Test changes in a local Odoo 17 instance.
- Verify form views, workflows, and approvals behave as expected.
- Ensure accounting entries are created correctly when loans are approved.
- Confirm reports and wizards work without errors.

## Submitting Changes

1. Create a feature branch from `main` or the relevant base branch.
2. Make your changes and test them locally.
3. Commit with clear, descriptive messages.
4. Open a pull request against the main repository.

### PR Guidelines

- Describe the problem and your solution clearly.
- List any installation or upgrade steps required.
- Mention any modules or dependencies added or changed.
- Include notes on how you validated the changes.

## Issues and Bug Reports

- Provide a concise summary of the issue.
- Include steps to reproduce the behavior.
- Attach relevant log snippets, screenshots, or traceback information.
- Specify whether the issue occurs during module install, use, or a specific workflow.

## Code Style

- Prefer PEP 8 compatible Python formatting.
- Use Odoo naming conventions and field definitions.
- Keep XML indentation consistent and readable.
- Avoid large unrelated changes in a single commit.

## License

This module follows the same licensing terms as the parent repository. If you are submitting contributions, ensure they are compatible with the module license.
