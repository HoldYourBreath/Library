"use strict";


$( document ).ready(function() {
    $('#user_id').on('keypress', function(e) {
        var code = e.keyCode || e.which;
        if(code==13){
            get_user_info();
        }
    });

    $('#getUser').on('click', function (e) {
        get_user_info();
    });
});

function get_user_info(user_id) {
    console.log("Get user information!");

}