odoo.define('contact_mail_redirect.basic_fields', function (require) {
    "use strict";

    var FieldEmail = require('web.basic_fields').FieldEmail;
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;

    FieldEmail.include({
        get_contact_leads: async function (self) {
            const contact = self._rpc({
                model: 'res.partner',
                method: 'search_read',
                domain: [['email', 'ilike', self.value.replace(/\s/g, '')]],
                limit: 1,
            });
            const lead = self._rpc({
                model: 'crm.lead',
                method: 'search_read',
                domain: [['email_from', 'ilike', self.value.replace(/\s/g, '')]],
                limit: 1,
            });
            return Promise.all([contact, lead])
        },
        _onClick: function (ev) {
            ev.stopPropagation();
            var self = this;
            if ($(ev.target).hasClass('mail_copy')) {
                navigator.clipboard.writeText(self.value);
                return
            }
            if (self.mode && self.mode == 'readonly' && self.value &&
                (!['res.partner', 'crm.lead'].includes(self.model) || 'default_parent_id' in self.record['context'])) {
                self.get_contact_leads(self).then((values) => {
                    var res_id;
                    var model;
                    var context = false;
                    if (values[0].length > 0) {
                        res_id = values[0][0]['id']
                        model = 'res.partner'
                    } else if (values[1].length > 0) {
                        res_id = values[1][0]['id']
                        model = 'crm.lead'
                    } else {
                        res_id = false
                        model = 'crm.lead'
                        context = { default_email_from: self.value }
                    }
                    self.do_action({
                        res_id: res_id,
                        res_model: model,
                        views: [[false, 'form']],
                        type: 'ir.actions.act_window',
                        context: context,
                    });
                });
            }
        },
        _renderReadonly: function () {
            if (this.value) {
                var copy_container = $("<span class='fa fa-clipboard mail_copy' style='position: absolute; padding: 3px 13px;'></span>");
                var self = this;
                self.$el.closest("." + self.className).text(self.value)
                    .addClass('o_form_uri o_text_overflow')
                    .attr('href', 'javascript:void(0)')
                    .append(copy_container);
            } else {
                this.$el.text('');
            }
        },
    })
})
