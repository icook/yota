function ajax_activate(form_id, error_callback, success_callback) {
    window.yota_ajax_options = { 
        success: function (jsonObj)  {
            // do some processing on the json that's returned
            if (jsonObj.success) {
                success_callback();
            } else {
                $('#' + form_id + " > *").find(":input").each(function() {
                    if (!(this.id in jsonObj.errors)) {
                        error_callback(this.id, false, {});
                    } else {
                        error_callback(this.id, true, jsonObj.errors[this.id]);
                    }
                });
            }
        },
        beforeSubmit: function(arr, form, options) {
            // go through our array and remove all the data items that haven't been marked as touched
            for (var i = arr.length-1; i > 0; i--) {
                // automatically pass all _ prefixed names
                if (arr[i].name[0] == '_')
                    continue;
                if (!window.visited[arr[i].name]) {
                    arr.splice(i, 1);
                }
            }
        },
        dataType: 'json'
    }; 
    $('#' + form_id).ajaxForm(window.yota_ajax_options);
}
