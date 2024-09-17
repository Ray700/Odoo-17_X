import jwt
import datetime
from odoo 17 import http
from odoo.http import request
from odoo.exceptions import AccessDenied

# Define a secret key to encode/decode JWT tokens
SECRET_KEY = 'admin'

class CustomerAPI(http.Controller):

    def _decode_jwt(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # Customer login endpoint
    @http.route('/api/customer/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        if not email or not password:
            return {'error': 'Email and password required'}
        
        # Find the user
        user = request.env['res.users'].sudo().search([('login', '=', email)])
        if not user or not user.sudo().check_password(password):
            return {'error': 'Invalid credentials'}
        
        # Create JWT token
        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token valid for 24 hours
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        return {'token': token}

    # Customer logout endpoint (JWT is stateless, so we just return a success message)
    @http.route('/api/customer/logout', type='json', auth='public', methods=['POST'], csrf=False)
    def logout(self, **kwargs):
        return {'message': 'Logged out successfully'}

    # Fetch all orders for the authenticated customer
    @http.route('/api/order', type='json', auth='public', methods=['GET'], csrf=False)
    def get_orders(self, **kwargs):
        token = kwargs.get('token')
        user_id = self._decode_jwt(token)

        if user_id:
            orders = request.env['sale.order'].sudo().search([('partner_id', '=', user_id)])
            order_data = [{'id': order.id, 'name': order.name, 'total': order.amount_total} for order in orders]
            return {'orders': order_data}
        else:
            return {'error': 'Unauthorized access'}

    # Fetch details for a specific order by its ID
    @http.route('/api/order/<int:order_id>', type='json', auth='public', methods=['GET'], csrf=False)
    def get_order(self, order_id, **kwargs):
        token = kwargs.get('token')
        user_id = self._decode_jwt(token)

        if user_id:
            order = request.env['sale.order'].sudo().browse(order_id)
            if order:
                return {
                    'order_id': order.id,
                    'order_name': order.name,
                    'order_total': order.amount_total
                }
            else:
                return {'error': 'Order not found'}
        else:
            return {'error': 'Unauthorized access'}

    # Fetch all payments for a specific order
    @http.route('/api/order/<int:order_id>/payments', type='json', auth='public', methods=['GET'], csrf=False)
    def get_payments(self, order_id, **kwargs):
        token = kwargs.get('token')
        user_id = self._decode_jwt(token)

        if user_id:
            payments = request.env['account.payment'].sudo().search([('invoice_ids.sale_order_id', '=', order_id)])
            payment_data = [{'id': p.id, 'amount': p.amount, 'date': p.payment_date} for p in payments]
            return {'payments': payment_data}
        else:
            return {'error': 'Unauthorized access'}

    # Fetch the invoice in PDF format
    @http.route('/api/order/invoice/<int:invoice_id>', type='http', auth='public', csrf=False)
    def get_invoice(self, invoice_id, **kwargs):
        token = kwargs.get('token')
        user_id = self._decode_jwt(token)

        if user_id:
            invoice = request.env['account.move'].sudo().browse(invoice_id)
            if invoice:
                pdf = request.env.ref('account.account_invoices').sudo().render_qweb_pdf([invoice_id])[0]
                pdfhttpheaders = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(pdf)),
                    ('Content-Disposition', f'attachment; filename=Invoice-{invoice.name}.pdf;')
                ]
                return request.make_response(pdf, headers=pdfhttpheaders)
            else:
                return {'error': 'Invoice not found'}
        else:
            return {'error': 'Unauthorized access'}
