# -*- coding: utf-8 -*-
{
    'name': "ts_sale_comparison",

    'summary': """
    Popup product comparison
        """,
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale_comparison'],

    # # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
    ],
    # 'qweb': ['static/src/xml/compare_them.xml'],
    'application': True,
    # only loaded in demonstration mode,
}
