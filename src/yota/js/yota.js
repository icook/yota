(function ($) {

    // The primary activator method for Yota. Is a wrapper around jQuery Form
    // plugin
    $.fn.yota_activate = function (options) {
        // set up a var to use when our form changes scope
        var form_obj = this;
        // default settings
        var settings = $.extend({  
            // Show errors with a bootstrap tooltip by default
            render_success: function (data, ids) {
                if (data.custom_success != undefined) {
                } else {
                    if (ids.error_id != undefined) {
                        $("#" + ids.error_id).show();
                        $("#" + ids.error_id).html(data.message);
                    }
                }
            },
            render_error: function (id, status, data) {
                // exit if there wasn't a proper id given
                if (id.elements[0] == undefined) {
                    console.log("There are no elements defined to deliver " +
                                "this error to!");
                    return;
                }
                // else, start tagging or removing respectively
                target_id = id.error_id;
                if (status == "no_error")
                    $('#' + target_id).fadeOut();

                if (status == "update" || status == "error") {
                    if (data.length > 1) {
                        var tip = '<ul>';
                        for (var key in data) {
                            tip += '<li>' + data[key]['message'] + '</li>';
                        }
                        tip += '</ul>';
                    } else
                        var tip = data[0]['message'];

                    $('#' + target_id).html(tip);
                    // Set the css styling
                    $('#' + target_id).removeClass();
                    $('#' + target_id).addClass(data[0]._type_class);
                    $('#' + target_id).fadeIn();
                }
            },
            piecewise: false,
            process_builtins: true
        }, options);

        // A book-keeping system to track currently displayed errors
        var errors_present = {};
        $(this).data('yota_errors_present', errors_present);

        // configuration options to go to jQuery Form plugin
        //   more information about the plugin can be found at:
        //   http://www.malsup.com/jquery/form/
        var ajax_options = { 
            // Called upon successful return of the AJAJ call
            success: function (jsonObj)  {
                // upon failure, deliver our error messages
                if (jsonObj.success == false) {
                    error_obj = jsonObj.errors;
                    for (var key in error_obj) {
                        if (key in errors_present) {
                            // update
                            settings.render_error(error_obj[key].identifiers,
                                        "update",
                                        error_obj[key].errors);
                        } else {
                            // new error
                            settings.render_error(error_obj[key].identifiers,
                                        "error",
                                        error_obj[key].errors);
                            // register the error in our bookkeeping system
                            errors_present[key] = error_obj[key].identifiers;
                        }
                    }

                    // remove the errors that weren't updated
                    for (var key in errors_present) {
                        if (!(key in error_obj)) {
                            settings.render_error(errors_present[key], "no_error", {});
                            delete errors_present[key];
                        }
                    }
                } else {
                    // remove all the errors. Either we just got new ones, or there
                    // were none.
                    for (var key in errors_present) {
                        settings.render_error(errors_present[key], "no_error", {});
                        delete errors_present[key];
                    }
                    // DEPRECATED - Scheduled for removal ~0.2.5
                    if (jsonObj.redirect != undefined) {
                        window.location.replace(jsonObj.redirect);
                        return;
                    }
                    if ('success_blob' in jsonObj) {
                        opts = jsonObj.success_blob;
                        if (settings.process_builtins == true) {
                            // Catch some builtin keys that and perform actions
                            // with them
                            if (opts.custom_success)
                                eval(opts.custom_success);
                            if (opts.reset_form == true)
                                $(form_obj)[0].reset();
                            if (opts.redirect)
                                window.location.replace(opts.redirect);
                            if (opts.ga_run) {
                                if (typeof(ga) === 'function')
                                    ga('send', 'event', opts.ga_run[0], opts.ga_run[1], opts.ga_run[2], opts.ga_run[3]);
                            }
                        }
                    } else {
                        opts = ''
                    }
                    // run the success callback and pass it details from yota
                    settings.render_success(opts, jsonObj.success_ids);
                }
            },
            beforeSubmit: function(arr, form, options) {
                // gets the list of visited nodes and adds them to the
                // submitted data
                var visited = $(form).data('yota_visited')
                var json = JSON.stringify(visited);
                arr.push({name: '_visited_names', value: json});
            },
            // ask the plugin to automatically give us an object on return
            dataType: 'json'
        };

        // attach the options to the form node for easy triggering of submit
        // later
        $(this).data('yota_ajax_options', ajax_options);

        if (settings.piecewise) {
            // Setup the listeners that will track nodes that have been "triggered"
            // This is what keeps piecewise validation from just flooding the user
            // with errors the instant they start typing
            var visited = {};
            $(this).data('yota_visited', visited);
            // loop over all elements in the form
            $(this).find(":input").each(function() {
                // preload our vars
                var trigger = $(this).data("piecewise");
                var name = $(this).attr("name");
                // if they are marked as triggerable
                if (trigger) {
                    $(this).on(trigger, function() {
                        visited[name] = true;
                        $(form_obj).ajaxSubmit(ajax_options);
                    });
                }
            });
        }

        // attach a slightly modified call to the submit button. This allows
        // the server side piecewise validation to recognize actual submisiion
        // properly
        $(this).submit(function () {
            // if this is piecewise, mark everything as visited since they
            // just submitted
            if (settings.piecewise) {
                $(this).find(":input").each(function() {
                    var name = $(this).attr("name");
                    visited[name] = true;
                });
            }
            $(this).ajaxSubmit($.extend({data: {'submit_action': 'true'}}, ajax_options));
            return false;  // don't submit
        });
        return this;
    }
}( jQuery ));
