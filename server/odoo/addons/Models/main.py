import string
from odoo import models, fields

class customerapi(models.Model):
    _name = 'customerapi'
    _description = "customer api"
    
    name = fields.Char(string"customer api")
    