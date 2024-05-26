(function(){
    if(!window.is_website){
        return;
    }
    function activate_purge(){
        let loc_obj = window.location;
        let server_url = loc_obj.origin + '';

        if(server_url.startsWith('http://localhost') || server_url.startsWith('http://127.0.0')){
            console.log('Purge clicks wont work');
        }

        else{
            $('#purge-menu a.purge').click(function(){
                let current_page = loc_obj + '';
                let purge_req_options = {
                    url: server_url + '/purge/cache',
                    data: {
                        url: current_page,
                    },
                    success: function(data){
                        alert(data);
                    },
                    error: function(e){
                        alert('Some error in purge');
                        console.log(e);
                    }
                }
                let el = $(this);
                if(el.hasClass('all')){
                    purge_req_options.data.url = 'all';
                }
                $.ajax(purge_req_options);
            });
        }
    }

    function check_user(){
        let user_class = 'o_connected_user';
        let org = window.location.origin + '';
        let options = {
            url: org + '/auth/get_user_id',
            beforeSend: function(a, b){
                console.log(b.url);
            },
            success: function(uid){
                if(!isNaN(uid)){
                    let user_menu_bar = $('#oe_main_menu_navbar');
                    user_menu_bar.css('display', 'grid');
                    if(!$('body').hasClass(user_class))
                    {
                        $('body').addClass(user_class);
                    }
                    console.log('User available '+uid);
                    $('button[data-target="#top_menu_collapse"],#edit-page-menu').css('visibility', 'visible');
                }
                else{
                    //console.log(uid,3);
                    if($('body').hasClass(user_class))
                    {
                        $('body').removeClass(user_class);
                    }
                    console.log('User unavailable');
                }
            },
            error:function(){
                //console.log(uid,3);
                $('body').removeClass(user_class);
            }
        }
        $.ajax(options);
    }

    if($('#purge-menu a.purge').length)
    {
        activate_purge();
    }

    check_user();
    console.log('after dj 3');
})()