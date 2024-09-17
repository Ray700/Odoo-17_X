# models/product_profit_report.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductProfitReport(models.TransientModel):
    _name = 'product.profit.report'
    _description = 'Product Profit Report for the Fiscal Year'

    fiscal_year_id = fields.Many2one('account.fiscal.year', string="Fiscal Year", required=True)

    def calculate_profit(self):
        """
        This method calculates the profit on each product by subtracting
        the total purchase cost from the total sales revenue for the fiscal year.
        """
        fiscal_year = self.fiscal_year_id
        start_date = fiscal_year.date_start
        end_date = fiscal_year.date_end

        # Fetch products and related sales/purchases
        products = self.env['product.product'].search([])

        profit_data = []
        for product in products:
            # Total sales revenue
            total_sales = sum(order_line.price_total for order_line in self.env['sale.order.line'].search([
                ('product_id', '=', product.id),
                ('order_id.date_order', '>=', start_date),
                ('order_id.date_order', '<=', end_date),
                ('order_id.state', 'in', ['sale', 'done'])  # Include confirmed and delivered sales
            ]))

            # Total purchase cost
            total_purchases = sum(order_line.price_total for order_line in self.env['purchase.order.line'].search([
                ('product_id', '=', product.id),
                ('order_id.date_order', '>=', start_date),
                ('order_id.date_order', '<=', end_date),
                ('order_id.state', 'in', ['purchase', 'done'])  # Include confirmed and delivered purchases
            ]))

            # Calculate profit
            profit = total_sales - total_purchases

            profit_data.append({
                'product_name': product.name,
                'total_sales': total_sales,
                'total_purchases': total_purchases,
                'profit': profit,
            })

        return profit_data
