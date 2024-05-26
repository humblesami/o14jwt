odoo.define('contact_mail_redirect.BasicRenderer', function (require) {
"use strict";

var BasicRenderer = require('web.BasicRenderer');

BasicRenderer.include({
    async _render() {
        await this._super(...arguments);
        if (!['res.partner', 'crm.lead'].includes(this.state.model)){
            var values = {}
            var fields = []
            for (const handle in this.allFieldWidgets) {
                this.allFieldWidgets[handle].forEach(widget => {
                    if(widget.attrs.widget == 'email' && widget.mode == 'readonly' && widget.value){
                        widget.$el.css('color', 'red')
                        values[widget.res_id] = [widget.$el, widget.value.replace(/\s/g, '')]
                    }
                });
            }
            if (!jQuery.isEmptyObject(values)){
               const contact = this._rpc({
                    model: 'res.partner',
                    method: 'search_mail_contact',
                    args: [0, values],
                });
                const lead = this._rpc({
                    model: 'crm.lead',
                    method: 'search_mail_contact',
                    args: [0, values],
                });
                const findEmail = function(emails, values){
                    for (const val in emails) {
                        for(const elem in values){
                            if(values[elem][1].toLowerCase() === emails[val][0].toLowerCase()){
                                values[elem][0].css('color', '#008784')
                            }
                        }
                    }
                }
                Promise.all([contact, lead]).then((result) => {
                    if (result[0].length > 0 || result[1].length > 0){
                        findEmail(result[0], values)
                        findEmail(result[1], values)
                    }
                });
            }
        }
    }
});

})