from odoo import fields, http
from odoo.http import request

class DashboardController(http.Controller):

    @http.route('/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        today = request.env['sale.order'].sudo().search([('commitment_date', '>=', fields.Date.today())])
        deliveries = [{'name': order.name, 'date': order.commitment_date} for order in today]

        payments = request.env['account.payment'].sudo().read_group(
            [('payment_date', '>=', fields.Date.today())],
            ['amount:sum', 'payment_date'],
            ['payment_date']
        )
        total_payments = [{'date': p['payment_date'], 'amount': p['amount']} for p in payments]

        return {
            'deliveries': deliveries,
            'payments': total_payments
        }
