from odoo import fields, models, api, Command
from datetime import date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
class EmployeeLoan(models.Model):
    _rec_name = 'employee_id'
    _name = 'employee.loan'
    _inherit=["mail.thread","mail.activity.mixin"]
    # employee details
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Job Position")
    # loan details
    loan_amount = fields.Float(required=True, tracking=True) 
    start_at = fields.Date(required=True, tracking=True)  
    installments_nums = fields.Integer(required=True, tracking=True, groups="employee_loan_task.employee_loan_manager_group") 
    monthly_Installment = fields.Float() # _compute field
    state = fields.Selection([
        ('draft','Draft'),
        ('panding','Panding'),
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('paid','Paid'),
    ],required=True, tracking=True)
    line_ids = fields.One2many('loan.lines','loan_id', tracking=True)
    # Wizard
    reject_reason = fields.Text(string="Reject Reason", readonly=True)
    # الربط مع الحسابات
    journal_id = fields.Many2one('account.journal', string="Payment Journal")
    loan_account_id = fields.Many2one('account.account',
                                      string="Loan Account",
                                      related='employee_id.loan_account_id',)
    move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)
    def action_draft(self):
        for rec in self:
            rec.state="draft"
    def action_panding(self):
        for rec in self:
            rec.state="panding"
    def action_approved(self):
        self.write({'state': 'approved'})
        for rec in self:
            if not rec.journal_id:
                raise ValidationError("Make sure that 'Payment Journal' has value.")
            if not rec.loan_account_id:
                raise ValidationError("Make sure that 'Loan account' has value.")
            if rec.loan_amount == 0 :
                raise ValidationError("Loan amount can't be less than or equal zero")
            
            line_ids = [
                # First line: Debtor (Employee advance account)
                Command.create({
                    'name': f"Employee loan: {rec.employee_id.name}",
                    'account_id': rec.employee_id.loan_account_id.id,
                    'debit': rec.loan_amount,
                    'credit': 0.0,
                }),
                # Line 2: Credit (Bank/Cash account of the journal)
                Command.create({
                    'name': f"Employee loan payment: {rec.employee_id.name}",
                    'account_id': rec.journal_id.default_account_id.id,
                    'debit': 0.0,
                    'credit': rec.loan_amount,
                }),
            ]
        # Preparing the accounting entry header data
            move_vals = {
            'move_type': 'entry',
            'date': rec.start_at, 
            'journal_id': rec.journal_id.id, 
            'ref': f"Employee loan verification record: {rec.employee_id.name}", # Statement
            'line_ids': line_ids,
        }
        move = self.env['account.move'].create(move_vals)
        rec.move_id = move.id
        loan_lines = []
        installment_amount = self.loan_amount / self.installments_nums
        current_date = self.start_at  
        for i in range(self.installments_nums):
            line_data = {
                'installment_date': current_date,
                'amount': installment_amount,
                'installments_num': i +1,
                'state': 'due' ,
            }
            loan_lines.append((0, 0, line_data))
            current_date += relativedelta(months=1)
        self.line_ids = loan_lines
     #  The action associated with the reject button
    def action_reject_loan(self):
        return {
            'name': 'Reason for Rejection',
            'type': 'ir.actions.act_window',
            'res_model': 'reject.loan.request', 
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_loan_id': self.id} 
        }
    def action_paid(self):
        for rec in self:
            rec.state="paid"
            
    # validation
    # Preventing the entry of a negative or zero advance amount.
    @api.constrains('loan_amount')
    def validate_loan_amount(self):
        for rec in self:
            if rec.loan_amount == 0:
                raise ValidationError("loan amount can't be equal 'Zero'")
            if rec.loan_amount < 0:
                raise ValidationError("loan amount can't be 'Negative number'")
    # Preventing the recording of past date
    @api.constrains('start_at')
    def validate_start_date(self):
        for rec in self:
            if rec.start_at: 
                current_date= fields.datetime.now().date()
                start_date = rec.start_at
                if start_date < current_date:
                    raise ValidationError ("start date mustn't be in the past")
    # Preventing requests for more than one loan            
    @api.constrains('employee_id','state')
    def validate_loans(self):
        for rec in self:
            if rec.state not in ('rejected','paid'):
                domain=[('employee_id','=',rec.employee_id.id),
                        ('id', '!=', rec.id),
                        ]
                duplicate_request = self.search(domain)
                if duplicate_request :
                    raise ValidationError ("this employee has another request")
    # cron job
    def installment_payment_date(self):
        today = date.today()
        unpaid_installments = self.env['loan.lines'].search([
        ('state', '=', 'due'),
        ('installment_date', '<=', today)])
        if unpaid_installments:
            unpaid_installments.write({'state': 'paid'})
            for line in unpaid_installments:
                if not line.loan_id or not line.loan_id.journal_id or not line.loan_id.employee_id:
                    continue
                move_vals = {
                    'journal_id': line.loan_id.journal_id.id, 
                    'date': fields.Date.today(),              
                    'ref': f"سداد قسط شهر {line.installment_date.strftime('%m/%Y')} - {line.loan_id.employee_id.name}",
                    'move_type': 'entry',                     
                    'line_ids': [
                        # 🔵 First line: Debit side -> The treasury or bank account into which the funds were deposited
                        (0, 0, {
                            'name': f"استقطاع قسط سلفة - {line.loan_id.employee_id.name}",
                            'partner_id': line.loan_id.employee_id.user_id.partner_id.id,
                            'account_id': line.loan_id.journal_id.default_account_id.id, 
                            'debit': line.amount,
                            'credit': 0.0,
                        }),
                        # 🔴 Second line: Credit side -> Loan account decreases by the installment amount
                        (0, 0, {
                            'name': f"تخفيض مديونية السلفة - {line.loan_id.employee_id.name}",
                            'partner_id': line.loan_id.employee_id.user_id.partner_id.id,
                            'account_id': line.loan_id.employee_id.loan_account_id.id,   
                            'debit': 0.0,
                            'credit': line.amount,
                        }),
                    ]
                }
                move = self.env['account.move'].create(move_vals)
                move.action_post() 
                line.write({
                'move_id': move.id 
                        })
                new_credit_line = move.line_ids.filtered(lambda l: l.credit > 0)
                original_debit_line = line.loan_id.move_id.line_ids.filtered(
                    lambda l: l.debit > 0 and l.account_id == line.loan_id.employee_id.loan_account_id.id and not l.reconciled
                )
                if new_credit_line and original_debit_line:
                    (new_credit_line + original_debit_line).reconcile()
class LoanLines(models.Model):
    _name = 'loan.lines'
    installments_num = fields.Integer()
    installment_date = fields.Date()
    amount = fields.Float()
    state = fields.Selection([
        ('due','Due'),
        ('paid','Paid'),
    ],default='due')
    loan_id = fields.Many2one('employee.loan')
    move_id = fields.Many2one('account.move', string="Journal Move", readonly=True)
