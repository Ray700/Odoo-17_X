{
    'name': 'Customer Dashboard',
    'version': '17.0.0.1',
    'category': 'Tools',
    'summary': 'Dashboard for showing upcoming deliveries and daily payments',
    'author': 'Ray',
    'depends': ['sale', 'account', 'web'],
    'data': [
        'views/dashboard_template.xml',
    ],
    'qweb': ['static/src/js/dashboard.js'],
    'installable': True,
    'application': True,
}
