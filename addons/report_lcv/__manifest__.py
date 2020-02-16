# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Reporte de Libro Ventas IVA',
    'version': '10.0.1.0',
    'sequence': 1,
    'category': 'Account',
    'description': """
        This module will help to generate invoice LCV Excel Report
""",
    'summary':'generate invoice lcv excel report',
    'author': 'Ing. Mauricio C.',
    'website': 'http://www.odoo.org.bo',
    'depends': ['sale','account'],
    'data': [
        'wizard/invoice_discount_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
