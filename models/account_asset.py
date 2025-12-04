# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

class AccountAsset(models.Model):
    _inherit = "account.asset"

    compania_relacionada_id = fields.Many2one('res.company', string='Compañía fiscal relacionada', index=True, ondelete='restrict')
    codigo = fields.Char(string="Código")
    numero_serie = fields.Char(string="Número de serie")
    departamento_id = fields.Many2one('hr.department', string='Departamento')
    tipo = fields.Selection(
        selection=[
            ('original', 'Original'),
            ('reavaluo', 'Reavalúo'),
        ],
        string="Tipo",
    )
    activo_padre_id = fields.Many2one('account.asset', string='Activo padre', domain="[('state','!=', 'model')]")
    sinc_id = fields.Integer(string="Id del Activo en la compañía relacionada")

    def unlink(self):
        for asset in self:
            activo_id = self.env['account.asset'].sudo().search([('sinc_id', '=', asset.id)], limit=1)
            if activo_id:
                activo_id.sinc_id = 0
        return super(AccountAsset, self).unlink()

    @api.onchange('compania_relacionada_id')
    def _onchange_compania_relacionada(self):
        activo_ids = self.env['account.asset'].search([('model_id', '=', self._origin.id), ('sinc_id', '>', 0)])
        if activo_ids:
            raise UserError("No se puede cambiar la Compañía fiscal relacionada a un Modelo de activo que tiene relacionados activos que ya fueron copiados.")

    def copiar_activo(self):
        for activo in self:

            if activo.sinc_id > 0:
                raise UserError("El activo '" + activo.name + "' ya fue creado con anterioridad en la compañía relacionada.")

            if not activo.model_id:
                raise UserError("Para poder copiar el activo '" + activo.name + "', este debe tener asignado un 'Modelo de activo'.")

            if not activo.model_id.compania_relacionada_id:
                raise UserError("El Modelo de activo '" + activo.model_id.name + "' debe tener asignada una compañía fiscal relacionada.")

            if activo.activo_padre_id and activo.id != activo.activo_padre_id.id:
                if activo.activo_padre_id.sinc_id == 0:
                    raise UserError("Para el activo '" + activo.name + "', su activo padre '" + activo.activo_padre_id.name + "' aún no ha sido creado en la compañía relacionada: '" + activo.model_id.compania_relacionada_id.name + "'")

                if activo.model_id != activo.activo_padre_id.model_id:
                    raise UserError("El activo '" + activo.name + "' y su activo padre '" + activo.activo_padre_id.name + "' deben tener configurado el mismo Modelo de activo")

            modelo_activo_relacionado_id = self.env['account.asset'].sudo().search([('company_id', '=', activo.model_id.compania_relacionada_id.id), ('name', '=', activo.model_id.name)], limit=1)
            if not modelo_activo_relacionado_id:
                raise UserError("Para poder copiar el activo '" + activo.name + "' debe existir un 'Modelo de activo' con el nombre '" + activo.model_id.name + "' en la compañía relacionada: '" + activo.model_id.compania_relacionada_id.name + "'")

            if activo.state != 'open':
                raise UserError("El activo '" + activo.name + "' debe tener estado 'En proceso' para poder ser copiado.")

            vals_list = {}
            vals_list['name'] = activo.name
            vals_list['company_id'] = modelo_activo_relacionado_id.company_id.id
            vals_list['model_id'] = modelo_activo_relacionado_id.id
            quetzal = self.env.ref('base.GTQ', raise_if_not_found=True)
            vals_list['original_value'] = activo.company_id.currency_id._convert(activo.original_value, quetzal, company=activo.company_id, date=activo.acquisition_date, round=False)
            vals_list['salvage_value'] = activo.company_id.currency_id._convert(activo.salvage_value, quetzal, company=activo.company_id, date=activo.acquisition_date, round=False)
            vals_list['already_depreciated_amount_import'] = activo.company_id.currency_id._convert(activo.already_depreciated_amount_import, quetzal, company=activo.company_id, date=activo.acquisition_date, round=False)
            vals_list['acquisition_date'] = activo.acquisition_date
            vals_list['codigo'] = activo.codigo
            vals_list['numero_serie'] = activo.numero_serie
            vals_list['tipo'] = activo.tipo

            activo_relacionado = self.env['account.asset'].sudo().create(vals_list)
            activo_relacionado._onchange_model_id()

            activo.sinc_id = activo_relacionado.id
            activo_relacionado.activo_padre_id = activo.activo_padre_id.sinc_id

