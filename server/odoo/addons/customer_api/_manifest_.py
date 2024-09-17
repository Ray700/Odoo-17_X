{
    'name': 'Customer API',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'API for Customer Login, Order Management, Payments',
    'author': 'Ray',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
