# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def search_mail_contact(self, values):
        emails = [values[email][1].lower() for email in values]
        self.env.cr.execute(
            "SELECT email_from FROM crm_lead WHERE LOWER(email_from) = ANY(%s)", (emails,))
        result = self.env.cr.fetchall()
        return result
