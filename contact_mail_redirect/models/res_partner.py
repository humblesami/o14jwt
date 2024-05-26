# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def search_mail_contact(self, values):
        emails = [values[email][1].lower() for email in values]
        self.env.cr.execute(
            "SELECT email FROM res_partner WHERE LOWER(email) = ANY(%s)", (emails,))
        result = self.env.cr.fetchall()
        return result
