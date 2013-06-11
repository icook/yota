(function ( $ ) {

    // The primary activator method for Yota. Is a wrapper around jQuery Form
    // plugin
    $.fn.yota_activate = function (error_callback,
                                   success_callback,
                                   piecewise) {
        // configuration options to go to jQuery Form plugin
        //   more information about the plugin can be found at:
        //   http://www.malsup.com/jquery/form/
        
        // A book-keeping system to track currently displayed errors
        errors_present = {};
        $(this).data('yota_errors_present', errors_present);

        ajax_options = { 
            // Called upon successful return of the AJAX call
            success: function (jsonObj)  {
                // remove all the errors. Either we just got new ones, or there
                // were none.
                for (var key in errors_present) {
                    error_callback(errors_present[key], false, {});
                    delete errors_present[key];
                }
                // if success is returned from Yota
                if (jsonObj.success) {

                    // if a redirect was requested...
                    if (jsonObj.redirect) {
                        window.location.replace(jsonObj.redirect);
                    } else {
                        // run the success callback and pass it details from yota
                        success_callback(jsonObj.success_blob);
                    }
                // upon failure, deliver our error messages
                } else {
                    error_obj = jsonObj.errors;
                    for (var key in error_obj) {
                        // now generate our new error message
                        error_callback(error_obj[key].identifiers,
                                       true,
                                       error_obj[key].errors);
                        // register the error in our bookkeeping system
                        errors_present[key] = error_obj[key].identifiers;
                    }
                }
            },
            // ask the plugin to automatically give us an object on return
            dataType: 'json'  
        }; 

        // attach the options to the form node for easy triggering of submit
        // later
        $(this).data('yota_ajax_options', ajax_options);

        if (piecewise) {
            // Setup the listeners that will track nodes that have been "triggered"
            // This is what keeps piecewise validation from just flodding the user
            // with errors the instant they start typing

            visited = {};
            $(this).data('yota_visited', visited);
            // loop over all elements in the form
            var form_obj = this;
            $(this).each(function() {
                // preload our vars
                var trigger = $(this).data("piecewise");
                var name = $(this).attr("name");
                // tag it as not visited
                visited[name] = false;
                // if they are marked as triggerable
                if (trigger) {
                    if (trigger == "blur") {
                        $(form_obj).blur($(this).yota_submit);
                    } else {
                        $(form_obj).keyup($(this).yota_submit);
                    }
                }
            });
        }
        // attach a slightly modified call to the submit button. This allows
        // piecewise validation to recognize properly
        $(this).ajaxForm($.extend({data: {'submit_action': 'true'}}, window.yota_ajax_options));
    }

    $.fn.yota_submit = function () {
        opt = $(this).data('yota_ajax_options');
        $(this).ajaxSubmit(opt);
    }
}( jQuery ));
