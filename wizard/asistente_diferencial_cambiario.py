# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _, Command
import logging

class AsistenteDiferencialCambiario(models.TransientModel):
    _name = 'texpasa.asistente_diferencial_cambiario'
    _description = 'Diferencial Cambiario'

    company_id = fields.Many2one("res.company", string="Compañía a Enviar Diferencial", required=True)

    def generar_diferencial(self):
        for wizard in self:
            facturas = self.env.context.get('active_ids')
            for factura in self.env['account.move'].browse(facturas):
                if factura.currency_id == factura.company_id.currency_id:
                    for pago in factura.matched_payment_ids:
                        valor_fecha_factura = self.company_id.currency_id._convert(pago.amount, factura.currency_id, company=self.company_id, date=factura.invoice_date, round=False)
                        valor_fecha_pago = self.company_id.currency_id._convert(pago.amount, factura.currency_id, company=self.company_id, date=pago.date, round=False)

                        diferencial = valor_fecha_pago - valor_fecha_factura

                        asiento = self.env['account.move'].with_company(self.company_id).create({
                            'ref': 'Diferencial cambiaro entre compañías Texpasa',
                            'journal_id': self.company_id.currency_exchange_journal_id.id,
                            'company_id': self.company_id.id,
                            'date': pago.date
                        })
                        asiento.line_ids = [Command.create({
                            'name': 'Diferencial ambiaro entre compañías Texpasa',
                            'account_id': factura.with_company(self.company_id).partner_id.property_account_receivable_id.id,
                            'debit': abs(diferencial) if diferencial > 0 else 0,
                            'credit': abs(diferencial) if diferencial < 0 else 0,
                        }), Command.create({
                            'name': 'Diferencial ambiaro entre compañías Texpasa',
                            'account_id': self.company_id.income_currency_exchange_account_id.id,
                            'debit': abs(diferencial) if diferencial < 0 else 0,
                            'credit': abs(diferencial) if diferencial > 0 else 0,
                        })]
                        logging.warning(asiento)

        return True
