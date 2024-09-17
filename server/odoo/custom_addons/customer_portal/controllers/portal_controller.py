# controllers/portal_controller.py
import hashlib
import hmac
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

SECRET_KEY = 'your_secret_key_for_access_token'

class CustomerPortalController(CustomerPortal):

    # Generate a secure token for each order
    def _generate_access_token(self, order_id):
        data = f'{order_id}'.encode('utf-8')
        token = hmac.new(SECRET_KEY.encode('utf-8'), data, hashlib.sha256).hexdigest()
        return token

    # Validate the access token from the URL
    def _validate_access_token(self, token, order_id):
        expected_token = self._generate_access_token(order_id)
        return hmac.compare_digest(token, expected_token)

    # Portal order view with the token
    @http.route(['/portal/order/<int:order_id>/<string:token>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, token, **kwargs):
        if not self._validate_access_token(token, order_id):
            return request.render("website.404")  # Render 404 if the token is invalid

        # Fetch the order and related data
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order:
            return request.render("website.404")  # Render 404 if order not found

        order_lines = order.order_line.sudo()
        products_received = [line for line in order_lines if line.qty_delivered >= line.product_uom_qty]
        payments = request.env['account.payment'].sudo().search([('invoice_ids.sale_order_id', '=', order_id)])

        values = {
            'order': order,
            'order_lines': order_lines,
            'products_received': products_received,
            'payments': payments,
        }
        return request.render('customer_portal.portal_order_summary', values)

    # API to generate the secure order link
    @http.route(['/portal/order/link/<int:order_id>'], type='json', auth='user')
    def generate_order_link(self, order_id):
        token = self._generate_access_token(order_id)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        order_link = f"{base_url}/portal/order/{order_id}/{token}"
        return {'order_link': order_link}
