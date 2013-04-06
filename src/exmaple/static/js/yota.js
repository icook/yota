function ajax_activate(form_id, error_callback, success_callback) {
    var options = { 
        success: function (jsonObj)  { 
            // do some processing on the json that's returned
            if (jsonObj.success) {
                success_callback();
            } else {
                for (var key in jsonObj.errors) {
                    var obj = jsonObj.errors[key];
                    error_callback(key, true, obj);
                }
                for (var i = 0; i < jsonObj.valid.length; i++) {
                    error_callback(jsonObj.valid[i], false, {});
                }
            }
        },
        dataType: 'json'
    }; 
    $('#' + form_id).ajaxForm(options);
}
