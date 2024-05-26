# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class Controller(http.Controller):
    @http.route('/mail/message/update_content', methods=['POST'], type='json', auth='public')
    def mail_message_update_content(self):
        params = request.jsonrequest['params']
        message_id = params['message_id']
        body = params['body']
        message_sudo = request.env['mail.message'].browse(message_id).sudo()
        message_sudo.body=body
        res = {
            'id': message_sudo.id,
            'body': message_sudo.body,
        }
        return res