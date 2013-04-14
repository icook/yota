function ajax_activate(form_id, error_callback, success_callback) {
    var options = { 
        success: function (jsonObj)  {
            alert("sdfomsdflkgfdsg");
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
        beforeSubmit: function(arr, $form, options) {
            // go through our array and remove all the data items that haven't been marked as touched
            for (var i = 0; i < form.length; i++) {
                if (form[i].name in window.visited)
                    form.splice(i, 1);
            }
        },
        dataType: 'json'
    }; 
    $('#' + form_id).ajaxForm(options);
}
