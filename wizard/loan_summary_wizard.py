from odoo import models, fields, api
import io
import base64
import xlsxwriter


class LoanSummaryWizard(models.TransientModel):
    _name = 'loan.summary.wizard'
    _description = 'Employee Loan Summary Wizard'

    # حقول التصفية والفلاتر
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Status')
    def action_generate_excel(self):
        self.ensure_one()
        
        # 1. بناء الشروط (Domain) بناءً على المدخلات في الـ Wizard
        domain = []
        if self.date_from:
            domain.append(('start_at', '>=', self.date_from))
        if self.date_to:
            domain.append(('start_at', '<=', self.date_to))
        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))
        if self.state:
            domain.append(('state', '=', self.state))

        # جلب سجلات السلف بناءً على الفلتر
        loans = self.env['employee.loan'].search(domain)

        # 2. إعداد الذاكرة المؤقتة لملف الإكسيل
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Loan Summary')

        # 3. إعداد التنسيقات (Formats)
        # worksheet.set_direction(1)  # 1 تعني اتجاه من اليمين لليسار ليناسب اللغة العربية
        
        title_format = workbook.add_format({
            'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 
            'bg_color': '#1f4e78', 'font_color': 'white'
        })
        header_format = workbook.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 
            'bg_color': '#f2f2f2', 'border': 1
        })
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        num_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'})
        total_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#e2efda', 'num_format': '#,##0.00'
        })

        # ضبط عروض الأعمدة لتناسب العناوين الجديدة
        worksheet.set_column('A:A', 6)   # م
        worksheet.set_column('B:B', 25)  # اسم الموظف
        worksheet.set_column('C:C', 20)  # الإدارة
        worksheet.set_column('D:D', 15)  # إجمالي السلفة الأصلية
        worksheet.set_column('E:E', 15)  # قيمة القسط الحالي
        worksheet.set_column('F:F', 15)  # تاريخ استحقاق القسط
        worksheet.set_column('G:G', 15)  # حالة القسط
        worksheet.set_column('H:H', 22)  # الرصيد المتبقي التراكمي

        # 4. كتابة العنوان الرئيسي
        worksheet.merge_range('A1:H2', 'تقرير تفصيلي بحركة أقساط السلف والأرصدة المتناقصة', title_format)

        # 5. كتابة العناوين للأعمدة (تمت إعادة الهيكلة لتصبح تفصيلية)
        headers = ['#', 'اسم الموظف', 'القسم / الإدارة', 'إجمالي السلفة', 'قيمة القسط', 'تاريخ الاستحقاق', 'حالة القسط', 'الرصيد المتبقي من السلفة']
        for col_num, header in enumerate(headers):
            worksheet.write(3, col_num, header, header_format)

        # 6. كتابة البيانات التفصيلية للأقساط وحساب الرصيد المتناقص
        row_idx = 4
        counter = 1
        
        for loan in loans:
            # نبدأ بوضع إجمالي السلفة كقيمة مرجعية للرصيد التراكمي المتبقي للموظف الحالي
            running_balance = loan.loan_amount 
            
            # ترتيب خطوط الأقساط بالتاريخ لضمان صحة كشف الحساب التناقصي للمحاسب
            ordered_lines = loan.line_ids.sorted(key=lambda l: l.installment_date)
            
            for line in ordered_lines:
                # إذا كان القسط مدفوعاً، نقوم بخصمه تلقائياً من الإجمالي التراكمي
                if line.state == 'paid':
                    running_balance -= line.amount
                
                # جلب حالة القسط بشكل نصي معرب مفهوم من الـ selection
                line_state_label = dict(line._fields['state'].selection).get(line.state, line.state)

                worksheet.write(row_idx, 0, counter, cell_format)
                worksheet.write(row_idx, 1, loan.employee_id.name or '', cell_format)
                worksheet.write(row_idx, 2, loan.employee_id.department_id.name or '', cell_format)
                worksheet.write(row_idx, 3, loan.loan_amount, num_format)     # السلفة الأصلية ثابتة في أسطر الموظف للرجوع إليها
                worksheet.write(row_idx, 4, line.amount, num_format)          # قيمة القسط الحالي
                worksheet.write(row_idx, 5, str(line.installment_date) if line.installment_date else '', cell_format) # موعد استحقاق هذا القسط
                worksheet.write(row_idx, 6, line_state_label, cell_format)    # مدفوع أم غير مدفوع
                worksheet.write(row_idx, 7, running_balance, num_format)      # الرصيد المتبقي التناقصي بعد معالجة القسط
                
                row_idx += 1
                counter += 1

        # 7. سطر الإجماليات للمبالغ والمدفوعات
        worksheet.merge_range(f'A{row_idx+1}:D{row_idx+1}', 'إجمالي قيمة الأقساط المدرجة بالتقرير', header_format)
        worksheet.write_formula(row_idx, 4, f'=SUM(E5:E{row_idx})', total_format) # مجموع عمود قيمة الأقساط
        
        # تنسيق بقية خلايا سطر الإجمالي ليكون الشكل العام منسقاً محاسبياً
        worksheet.write(row_idx, 5, '', total_format)
        worksheet.write(row_idx, 6, '', total_format)
        worksheet.write(row_idx, 7, '', total_format)

        workbook.close()
        output.seek(0)

        # 8. توليد تحميل الملف تلقائياً للمستخدم
        file_data = base64.b64encode(output.read())
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Detailed_Loan_Installments_Report.xlsx',
            'type': 'binary',
            'datas': file_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }