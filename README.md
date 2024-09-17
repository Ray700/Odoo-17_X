# Odoo 17 X
The above solution is designed to address the challeges posed by Company X, it is a solution within the Odoo ecosystem using Odoo 17, focusing on the required functionalities such as Client API development, Dashboard, Pivot Views, Calendar Views, Portal Views, and a profit Report.

## Table of contents
- [Installation](installation)
- [Customer API Module](Customer API Module)
- [Customer Dashboard Module](Customer Dashboard Module)
- [Customer Portal Module](Customer Portal Module)
- [Profit Report Module](Profit Report Module)

## installation
Instructions on how to install and set up Odoo 17.
log in to the server and update.
secure server
Install python 3 and it's dependencies.
Setup database serever(PostgreSQL).
System user.
Clone Odoo source from Github Repository.
Install required python packages.
Install wkhtmltopdf.
Setup configuration file.

## Customer API Module
Endpoint /api/customer/login and /api/customer/logout
Endpoint /api/order and /api/order/<order_id>
Orders – fetch order_id
Endpoint /api/order/<order_id>/payments - tracking payments.
Endpoint /api/order/invoice/<invoice_id> - invoice management.

## Customer Dashboard Module
Addons on odoo directory - customer_dashboard.
manifest file - _manifest_.py.
controllers/dashboard_controller.py.
views/dashboard_template.xml.
OWL - static/src/js/dashboard.js.
Template - dashboard_template.xml.

## Customer Portal Module.
Module initialization - _init_.py.
Manifest file - _manifest_.py.
Controllers/portal_controller.py.
Views/portal_order_template.xml.
Security/ir.model.access.csv

## Profit Report Module
Initialization file - _init_.py.
Module manifest - _manifest_.py.
models/product_profit_report.py.
reports/product_profit_template.xml.
data/report_actions.xml.
Controllers/report_controller.py


