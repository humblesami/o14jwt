odoo.define('mail_message.edit', function (require) {
    'use strict';
    const components = {
        Message: require('mail/static/src/components/message/message.js'),
    }

    const { patch } = require('web.utils');
    patch(components.Message, 'mail_message.edit', {
        _constructor() {
            this._super(...arguments);
        },
        async updateContent( body, attachment_ids=[] ) {
            let self = this;
            const messageData = await self.env.services.rpc({
                route: '/mail/message/update_content',
                params: {
                    body: body,
                    attachment_ids: [],
                    message_id: self.message.id,
                },
            });
            if (!this.messaging) {
                return;
            }
            console.log(self);
            //this.messaging.models['mail.message'].insert(messageData);
            this.env.models['mail.message'].insert(messageData);
        },
        updated_message: '',
        messageActionList_onClickEdit1(ev) {
            console.log('edit click ManyMore');
            ev.stopPropagation();

            let textInputContent = this.updated_message;
            let lim = $(ev.target).closest('.o_MessageList_item');

            if(!textInputContent){
                const parser = new DOMParser();
                const htmlDoc = parser.parseFromString(this.message.body.replaceAll('<br>', '\n').replaceAll('</br>', '\n'), "text/html");
                textInputContent = htmlDoc.body.textContent;
            }

            console.log(this.message.author.id);

            lim.find('.o_Message_content').html(
                `<textarea>${textInputContent}</textarea>`
            );
            let text_area = lim.find('textarea').focus();
            text_area.keyup(ev1=>{
                let el_val = text_area.val();
                if(ev1.keyCode == 13 && !ev1.shiftKey){
                    let message_body = `<div class="o_Message_prettyBody"><p>${el_val}</p></div>`;
                    lim.find('.o_Message_content').html(message_body);
                    this.updated_message = el_val;
                    this.updateContent(el_val);
                }
                if(ev1.keyCode == 27){
                    lim.find('.o_Message_content').html(
                        `<div class="o_Message_prettyBody"><p>${textInputContent}</p></div>`
                    );
                }
            });
        }
    })
});
