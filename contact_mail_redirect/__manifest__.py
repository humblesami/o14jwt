# -*- coding: utf-8 -*-

{
    'name': 'Contact Mail Redirect',
    'category': 'Base',
    'version': '14.0.1.0.0',
    'author': 'Alex Esteves',
    'license': 'AGPL-3',
    'summary': 'Module for redirecting mail clicking to contacts.',
    'description': """
        Module for redirecting mail clicking to contacts.
    """,
    'depends': [
        'base',
        'crm',
    ],
    'data': [
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
