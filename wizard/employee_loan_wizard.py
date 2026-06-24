from odoo import fields, models
from odoo.exceptions import ValidationError
class RejectLoanRequest(models.TransientModel):
    _name="reject.loan.request"
    loan_id = fields.Many2one("employee.loan")
    reason = fields.Char(required=True)
    def action_confirm(self):
        if not self.reason:
            raise ValidationError("Please provide a reason for rejection.")
        self.loan_id.write({
            'reject_reason': self.reason,
            'state': 'rejected' 
        })