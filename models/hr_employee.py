from odoo import fields, models

class Hr(models.Model):
    _inherit='hr.employee'
    # الربط مع الحسابات 
    loan_account_id = fields.Many2one('account.account', string="Default Loan Account")
    loan_count = fields.Integer(compute='_compute_loan_count', string='Loans')
    def _compute_loan_count(self):
        for rec in self:
            request_count = self.env['employee.loan'].search_count([
                ('employee_id', '=', rec.id)])
            rec.loan_count = request_count 
    def action_view_loan_requests(self):
        self.ensure_one()
        return {
            'name': 'Employee Loan',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.loan',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
        
        