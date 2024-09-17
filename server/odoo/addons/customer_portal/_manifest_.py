# __manifest__.py
{
    'name': 'Customer Portal',
    'version': '17.0',
    'summary': 'Customer portal to view orders,',
    'description': """
        This module provides a portal where customers can view their orders, 
        products received, and payments made. Customers can access the portal 
        via a secure link containing an access token.
    """,
    'category': 'Portal',
    'depends': ['base', 'sale', 'portal', 'account'],
    'data': [
        'views/portal_order_template.xml',
        'security/ir.model.access.csv',
    ],
    'assets': { 
        'web.assets_frontend': [
            '/customer_portal/static/src/css/custom_portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
