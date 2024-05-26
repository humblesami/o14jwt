import json
import requests
from odoo import http
from odoo.http import request


class Web(http.Controller):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        ir_model_access = request.env['ir.model.access']
        ir_model_access.call_cache_clearing_methods()
        return request.redirect('/web/login')

