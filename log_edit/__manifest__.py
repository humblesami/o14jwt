# -*- coding: utf-8 -*-
{
    'name': "log_edit",

    'summary': """
    """,
    'description': """
    """,

    # for the full list
    'author': 'sami',
    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/message.xml',
    ],
    # only loaded in demonstration mode
    'application': True,
}
