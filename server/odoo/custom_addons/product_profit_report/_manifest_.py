# __manifest__.py
{
    'name': 'Product Profit Report',
    'version': '17.0',
    'summary': 'Generate product profit reports for the fiscal year in DOCX format',
    'category': 'Reporting',
    'author': 'Ray',
    'depends': ['base', 'sale', 'purchase', 'account'],
    'data': [
        'reports/product_profit_template.xml',   # QWeb template for the report
        'data/report_actions.xml',               # Report action for printing
    ],
    'installable': True,
    'application': False,
}
