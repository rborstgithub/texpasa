# -*- coding: utf-8 -*-
{
    'name': "Texpasa",
    'summary': """ Funcionalidades extras para Texpasa """,
    'description': """
        Funcionalidades extras para Texpasa
    """,
    'author': "Aquih",
    'website': "http://www.aquih.com",
    'category': 'Uncategorized',
    'version': '1.3',
    'depends': ['account', 'account_asset', 'hr'],
    'data': [
        'wizard/asistente_diferencial_cambiario_views.xml',
        'views/account_views.xml',
        'views/account_asset_views.xml',
        'views/report_payment1.xml',
        'views/reports.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'Other OSI approved licence',
}
