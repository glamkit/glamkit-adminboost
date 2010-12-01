var no_conflict;

if (window.$){
    no_conflict = false;
} else {
    no_conflict = true;
}

var sortable_jquery = $.noConflict(no_conflict);

function init_sortable_inlines(inlines) {
    (function($){
        $(document).ready(function(){
            $.each(inlines, function(i, inline){
                
                var prefix = inline[0];
                var order_field;
                
                if (inline[1] == undefined) {
                    order_field = 'order';
                }
                else {
                    order_field = inline[1]; 
                }
                
                // remove order fields from the form
                var $group = $("#" + prefix + "-group");
                if ($group.length === 0){
                    return true; // continue iteration
                }
                
                // add hidden fields container
                var $hidden = $("<div class='hidden_order_fields'></div>");
                $hidden.appendTo($group);
                
                var arrow = $('<span class="ui-icon ui-icon-arrowthick-2-n-s adminboost-sortable-inlines-handle"></span>');
                
                var createUpdater = function(prefix, $group, $hidden){
                    /*
                    Unfortunately this ugly function factory is indeed necessary
                    Otherwise, function binded to $("submit").click (see the bottom of this file)
                    will contain a reference, not a value and in the end instead of calling as many
                    functions as there are prefixes, it will call same one many times.                                
                    */
                    
                    return function(event, ui){
                        
                        var selector;
                        if ($group.inline_type == "tabular") {
                            selector = "tr";
                        }
                        else {
                            selector = "div";
                        }
                        
                        // onUpdate event - update hidden fields
                        var txt = "";
                        var i = 0;
                        $group.find(selector + "[class~=dynamic-" + prefix + "]").each(function(i, domEl){
                            var $row = $(domEl);
                            $row.find("." + order_field).remove();
                            var row_num = $row.find("input:first").attr("name").match(/[0-9]+/);
                            if ($row.hasClass("empty-form")){
                                return true; // continue
                            }
                            
                            if ($group.inline_type == "tabular") {
                                // set colors, so the list doesn't look all weird
                                if (i % 2 == 0){
                                    $row.removeClass("row2").addClass("row1");
                                }
                                else{
                                    $row.removeClass("row1").addClass("row2");
                                }
                            }
                            
                            txt += "<input type='hidden' name='" + prefix + "-" + row_num + "-" + order_field + "' value='" + i + "' />";
                            i++;
                        });
                        $hidden.html(txt);
                    };
                };
                
                if ($group.find(".tabular").length > 0) {
                    
                    $group.find("table").prepend($("<tr>").addClass("adminboost-sortable-inlines-placeholder"));
                    
                    
                    $group.inline_type = "tabular";
                    
                    $group.find("th").filter(function(index) {
                        return $(this).text().toLowerCase() == order_field
                    }).remove();
                    
                    $group.find("th[colspan=2]").removeAttr("colspan");
                    $group.find("th:first").attr("colspan", "2");
        
                    $group.find("tr[class!=add-row]").each(function(){
                        $(this).find("td:first").prepend(arrow.clone());
                    });
                    $("<tbody></tbody>").appendTo($group.find("table")).append($group.find(".add-row").remove());
        
                    // add sortable from jqueryui
                    $group.find("table tbody:first").sortable({
                        update: createUpdater(prefix, $group, $hidden),
                        items: 'tr[class!=add-row]',
                        handle: "td:first",
                        distance: 6,
                        placeholder: "adminboost-sortable-inlines-tabular-placeholder",
                        forcePlaceholderSize: true
                    });
                }
                else {
                    $group.inline_type = "stacked";
                    
                    $group.find(".form-row." + order_field).remove();
    
                    $group.children(".inline-related").each(function(){
                        $(this).children("h3").prepend(arrow.clone());
                    });
                    // add sortable from jqueryui
                    $group.sortable({
                        update: createUpdater(prefix, $group, $hidden),
                        items: ".inline-related",
                        handle: ".adminboost-sortable-inlines-handle",
                        distance: 6,
                        placeholder: "adminboost-sortable-inlines-stacked-placeholder",
                        forcePlaceholderSize: true,
                        start: function(event, ui) {
                            $(ui.item).children().not("h3").hide();
                        },
                        stop: function(event, ui) {
                            $(ui.item).children().not("h3").fadeIn(500);
                        }
                    });
                }
                createUpdater(prefix, $group, $hidden)();
                
                $("form").submit(function(){
                    createUpdater(prefix, $group, $hidden)();
                });
            });
        });
    })(sortable_jquery);
}
