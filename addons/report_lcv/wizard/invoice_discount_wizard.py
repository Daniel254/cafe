# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
#========For Excel========
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64
# =====================

class invoice_discount_wizard(models.TransientModel):
    _name = "invoice.discount.wizard"

    @api.model
    def _get_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _get_from_date(self):
        date = datetime.now()
        month = date.month
        if date.month < 10:
            month = '0'+str(date.month)
        date = str(date.year)+'-'+str(month)+'-01'
        return date

    @api.model
    def _get_to_date(self):
        date = datetime.now()
        m_range = calendar.monthrange(date.year,date.month)
        month = date.month
        if date.month < 10:
            month = '0'+str(date.month)
        date = str(date.year)+'-'+str(month)+'-'+str(m_range[1])
        return date

    _states = [('draft','Draft'),('open','Open'),('paid','Paid'),('open_paid','Open and Paid')]

    start_date = fields.Date(string='Fecha Inicial', required="1", default=_get_from_date)
    end_date = fields.Date(string='Fecha Final', required="1", default=_get_to_date)
    state  = fields.Selection(_states, string='Estado', default='open_paid', required="1")
    excel_file = fields.Binary('Excel File')
    inv_type = fields.Selection([('out_invoice','Customer Invoice'),
                                 ('out_refund','Customer Refund'),
                                 ('in_invoice','Vendor Invoice'),
                                 ('in_refund','Vendor Refud'),
                                 ('out_invoice_refund','Customer Invoice and Refund'),
                                 ('in_invoice_refund','Vendor Invoice and Refund')], string='Invoice Type', required="1", default='out_invoice')


    @api.multi
    def get_style(self):
        main_header_style = easyxf('font:height 300;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz left;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")


        text_left = easyxf('font:height 200; align: horiz left;'
                            "borders: top thin,left thin,right thin,bottom thin")

        text_right = easyxf('font:height 200; align: horiz right;'
                            "borders: top thin,left thin,right thin,bottom thin", num_format_str='0.00')

        text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;'
                                "borders: top thin,left thin,right thin,bottom thin")

        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;'
                                 "borders: top thin,left thin,right thin,bottom thin", num_format_str='0.00')
        text_center = easyxf('font:height 200; align: horiz center;'
                             "borders: top thin,left thin,right thin,bottom thin")

        return [main_header_style, left_header_style,header_style, text_left, text_right, text_left_bold, text_right_bold, text_center]

    @api.multi
    def create_excel_header(self,worksheet,main_header_style,header_style,text_left,row):
        worksheet.write_merge(0, 1, 3, 4, 'Reporte Libro de Ventas', main_header_style)
        row = row

        company_id = self.env.user.company_id
        name = company_id.name +'\n'
        if company_id.street:
            if name:
                name = name + str(company_id.street) + '\n'
            else:
                name = str(company_id.street) + '\n'

        worksheet.write_merge(2, 4, 0, 2, name, text_left)

        row += 5
        return worksheet, row

    @api.multi
    def get_invoice(self):
        domain = [('date_invoice','>=',self.start_date),('date_invoice','<=',self.end_date)]
        if self.state == 'draft':
            domain.append(('state','=','draft'))
        elif self.state == 'open':
            domain.append(('state','=','open'))
        elif self.state == 'paid':
            domain.append(('state','=','paid'))
        elif self.state == 'open_paid':
            domain.append(('state','in',['open','paid']))

        if self.inv_type:
            if self.inv_type in ['out_invoice','in_invoice','out_refund','in_refund']:
                domain.append(('type','=',self.inv_type))
            else:
                if self.inv_type == 'out_invoice_refund':
                    domain.append(('type','in',['out_invoice','out_refund']))
                elif self.inv_type == 'in_invoice_refund':
                    domain.append(('type','in',['in_invoice','in_refund']))

        invoice_ids = self.env['account.invoice'].search(domain, order="number")
        return invoice_ids


    @api.multi
    def create_excel_table(self,worksheet,header_style,text_left,text_right,text_left_bold,text_right_bold,text_center,row):
        row = row + 2
        col=0
        worksheet.write(row,col, 'NRO', header_style)
        worksheet.write(row,col+1, 'FECHA DE LA FACTURA', header_style)
        worksheet.write(row,col+2, 'NRO DE LA FACTURA', header_style)
        worksheet.write(row,col+3, 'NRO DE AUTORIZACION', header_style)
        worksheet.write(row,col+4, 'ESTADO', header_style)
        worksheet.write(row,col+5, 'NIT O CI CLIENTE', header_style)
        worksheet.write(row,col+6, 'NOMBRE O RAZON SOCIAL', header_style)
        worksheet.write(row,col+7, 'IMPORTE TOTAL DE LA VENTA', header_style)
        worksheet.write(row,col+8, 'IMPORTE ICE IEHD IPJ TASAS OTROS NO SUJETOS AL IVA', header_style)
        worksheet.write(row,col+9, 'EXPORTACIONES Y OPERACIONES EXENTAS', header_style)
        worksheet.write(row,col+10, 'VENTAS GRAVADAS A TASA CERO', header_style)
        worksheet.write(row,col+11, 'SUBTOTAL', header_style)
        worksheet.write(row,col+12, 'DESCUENTOS BONIFICACIONES Y REBAJAS SUJETAS AL IVA', header_style)
        worksheet.write(row,col+13, 'IMPORTE BASE PARA DEBITO FISCAL', header_style)
        worksheet.write(row,col+14, 'DEBITO FISCAL', header_style)
        worksheet.write(row,col+15, 'CODIGO DE CONTROL', header_style)

        row+=1
        invoice_ids = self.get_invoice()
        col=0
        t_sub_total= t_debito_fiscal= debito_fiscal= t_discount= t_discount_bs= t_total = 0
        count = 0
        for invoice in invoice_ids:
            count += 1
            worksheet.write(row,col, count, text_center)
            date = ''
            if invoice.date_invoice:
                date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d')
                date = datetime.strftime(date, "%d-%m-%Y")
                worksheet.write(row,col+1, date, text_center)
            worksheet.write(row,col+2, invoice.number or '', text_center)
            worksheet.write(row,col+3, invoice.autorizacion or '', text_center)
            worksheet.write(row,col+4, invoice.state or '', text_center)
            worksheet.write(row,col+5, invoice.nit or '', text_center)
            worksheet.write(row,col+6, invoice.partner_id.name or '', text_left)
            subtotal = invoice.amount_total + invoice.amount_discount
            worksheet.write(row,col+7, subtotal or 0.0, text_right)
            t_sub_total += subtotal
            extra = 0
            worksheet.write(row,col+8, extra or 0.0, text_right)
            worksheet.write(row,col+9, extra or 0.0, text_right)
            worksheet.write(row,col+10, extra or 0.0, text_right)
            worksheet.write(row,col+11, subtotal or 0.0, text_right)
            worksheet.write(row,col+12, invoice.amount_discount or 0.0, text_right)
            t_discount_bs += invoice.amount_discount
            worksheet.write(row,col+13, invoice.amount_total or 0.0, text_right)
            t_total += invoice.amount_total
            debito_fiscal = invoice.amount_total * 0.13
            worksheet.write(row,col+14, debito_fiscal or '', text_right)
            t_debito_fiscal += debito_fiscal
            worksheet.write(row,col+15, invoice.code or '', text_right)
            row+=1

        if t_sub_total or  t_discount or t_discount_bs or t_total:
            worksheet.write_merge(row,row, 0, 6, 'TOTAL', text_left_bold)
            worksheet.write(row,col+7, t_sub_total or 0.0, text_right_bold)
            worksheet.write(row,col+8, t_sub_total or 0.0, text_right_bold)
            worksheet.write(row,col+9, t_sub_total or 0.0, text_right_bold)
            worksheet.write(row,col+10, t_sub_total or 0.0, text_right_bold)
            worksheet.write(row,col+11, t_sub_total or 0.0, text_right_bold)
            worksheet.write(row,col+12, t_discount_bs or 0.0, text_right_bold)
            worksheet.write(row,col+13, t_total or 0.0, text_right_bold)
            worksheet.write(row,col+14, t_debito_fiscal or 0.0, text_right_bold)
            row+=1
        return worksheet, row


    @api.multi
    def generate_excel(self):
        #====================================
        # Style of Excel Sheet
        excel_style = self.get_style()
        main_header_style = excel_style[0]
        left_header_style = excel_style[1]
        header_style = excel_style[2]
        text_left = excel_style[3]
        text_right = excel_style[4]
        text_left_bold = excel_style[5]
        text_right_bold = excel_style[6]
        text_center = excel_style[7]
        # ====================================

        # Define Wookbook and add sheet
        workbook = xlwt.Workbook()
        filename = 'Libro de Ventas.xls'
        worksheet = workbook.add_sheet('Libro de Ventas')
        for i in range(0,20):
            worksheet.col(i).width = 130 * 30
            if i == 0:
                worksheet.col(i).width = 100 * 30
            if i == 3:
                worksheet.col(i).width = 150 * 30
            if i == 6:
                worksheet.col(i).width = 350 * 30


        # Print Excel Header
        worksheet,row = self.create_excel_header(worksheet,main_header_style,header_style,text_left,3)

        # Print Excel Table
        worksheet,row = self.create_excel_table(worksheet,header_style,text_left,text_right,text_left_bold,text_right_bold,text_center,row)

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=invoice.discount.wizard&download=true&field=excel_file&id=%s&filename=%s' % (active_id, filename),
                'target': 'new',
            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
