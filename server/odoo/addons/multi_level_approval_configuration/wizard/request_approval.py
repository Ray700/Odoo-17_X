# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

import werkzeug.urls
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class RequestApproval(models.TransientModel):
    _name = 'request.approval'
    _description = 'Request Approval'

    name = fields.Char(string='Title', required=True)
    priority = fields.Selection(
        [('0', 'Normal'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority', default='0')
    request_date = fields.Datetime(
        string='Request Date', default=fields.Datetime.now, required=True)
    type_id = fields.Many2one(
        string="Type", comodel_name="multi.approval.type", required=True)
    description = fields.Html('Description')
    origin_ref = fields.Reference(
        string="Origin",
        selection='_selection_target_model')
    res_id = fields.Integer()
    res_model = fields.Char()

    budget_approver = fields.Many2one('res.users',domain="[('id','in',budget_approver_ids)]")
    budget_approver_ids = fields.Many2many('res.users')
    is_budget_approver = fields.Boolean(default=False)

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    def _get_obj_url(self, obj):
        base = 'web#'
        fragment = {
            'view_type': 'form',
            'model': obj._name,
            'id': obj.id
        }
        url = base + werkzeug.urls.url_encode(fragment)
        return url

    @api.model
    def default_get(self, fs):
        '''
        1. Get approval type
        2. Set the title as document's name
        3. Set origin
        '''
        res = super(RequestApproval, self).default_get(fs)
        ctx = self._context
        print ('___ ctx : ', ctx);
        model_name = ctx.get('active_model')
        res_id = ctx.get('active_id')
        types = self.env['multi.approval.type']._get_types(model_name)
        approval_type = self.env['multi.approval.type'].filter_type(
            types, model_name, res_id)
        if not approval_type:
            raise ValidationError(
                _('Data is changed! Please refresh your browser in order to continue !'))

        # Add the link to the source document inside the description.
        # in order to bypass the record rule on it
        record = self.env[model_name].browse(res_id)
        print ('___ record : ', record);
        record_name = record.display_name or _('this object')
        title = _('Request approval for {}').format(record_name)
        record_url = self._get_obj_url(record)
        if approval_type.request_tmpl:
            descr = _(approval_type.request_tmpl).format(
                record_url=record_url,
                record_name=record_name,
                record=record
            )
        else:
            descr = ''
        print ('___ record._name : ', record._name);
        if record._name == 'purchase.order':
            analytic_account_ids = record.order_line.mapped('account_analytic_id')
        elif record._name == 'account.move' and record.move_type != 'entry':
            analytic_account_ids = record.invoice_line_ids.mapped('analytic_account_id')
        elif record._name == 'account.move' and record.move_type == 'entry':
            analytic_account_ids = record.line_ids.mapped('analytic_account_id')
        else:
            analytic_account_ids = None
        budget_approver_ids = []
        if analytic_account_ids:
            analytic_account_id = analytic_account_ids[0]
            amount = record.amount_total
            if record._name == 'purchase.order':
                budget_lines = analytic_account_id.crossovered_budget_line.filtered(lambda l: l.date_from <=
                                                                                          record.date_order.date() <=
                                                                                          l.date_to)
            elif record._name == 'account.move' and record.move_type != 'entry':
                if not record.invoice_date:
                    raise ValidationError(_("Please Fill Invoice date"))
                budget_lines = analytic_account_id.crossovered_budget_line.filtered(lambda l: l.date_from <=
                                                                                          record.invoice_date <=
                                                                                          l.date_to)
            elif record._name == 'account.move' and record.move_type == 'entry':
                budget_lines = analytic_account_id.crossovered_budget_line.filtered(lambda l: l.date_from <=
                                                                                          record.date <=
                                                                                          l.date_to)
                amount = record.amount_total_in_currency_signed
                
            if budget_lines and budget_lines[0].crossovered_budget_id.approver_ids:
                budget_id = budget_lines[0].crossovered_budget_id
                approver_config_id = budget_id.approver_ids.filtered(
                    lambda l: l.min_limit <= amount and
                              l.max_limit >= amount)
                if approver_config_id:
                    budget_approver_ids = approver_config_id.user_id.ids
        print ('___ budget_approver_ids : ', budget_approver_ids);
        res.update({
            'name': title,
            'type_id': approval_type.id,
            'origin_ref': '{model},{res_id}'.format(
                model=model_name, res_id=res_id),
            'description': descr,
            'budget_approver_ids' : [(4, ap_id) for ap_id in budget_approver_ids],
            'is_budget_approver': True if budget_approver_ids and record._name != 'purchase.order' else False,
        })
        return res

    def action_request(self):
        '''
        1. create request
        2. Submit request
        3. update x_has_request_approval = True
        4. open request form view
        '''
        self.ensure_one()

        if not self.type_id.active or not self.type_id.is_configured or \
                not self.origin_ref.x_need_approval:
            raise ValidationError(
                _('Data is changed! Please refresh your browser in order to continue !'))
        if self.origin_ref.x_has_request_approval and \
                not self.type_id.is_free_create:
            raise ValidationError(
                _('Request has been created before !'))
        # create request
        ctx = self._context.copy()
        ctx.update({
            'approval_request':self
            })
        vals = {
            'name': self.name,
            'priority': self.priority,
            'type_id': self.type_id.id,
            'description': self.description,
            'origin_ref': '{model},{res_id}'.format(
                model=self.origin_ref._name,
                res_id=self.origin_ref.id),
            'res_id' : self.origin_ref.id,
            'res_model' : self.origin_ref._name
        }
        request = self.env['multi.approval'].with_context(ctx).create(vals)
        request.action_submit()

        # update x_has_request_approval
        self.env['multi.approval.type'].update_x_field(
            request.origin_ref, 'x_has_request_approval')

        return {
            'name': _('My Requests'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'multi.approval',
            'res_id': request.id,
        }
