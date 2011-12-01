// duplicated from contrib.admin's RelatedObjectLookups.js

function id_to_windowname(text) {
    text = text.replace(/\./g, '__dot__');
    text = text.replace(/\-/g, '__dash__');
    return text;
}

function get_edit_popup_id(edit_link){
    return edit_link.className.match(/\bedit_popup_(\w+)\b/)[1];
}

function showRelatedObjectEditPopup(triggeringLink) {
    var name = get_edit_popup_id(triggeringLink);
    name = id_to_windowname(name);
    var href;
    if (triggeringLink.href.search(/\?/) >= 0) {
        href = triggeringLink.href + '&pop=1&_popup=1&_edit_popup=1';
    } else {
        href = triggeringLink.href + '?pop=1&_popup=1&_edit_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

// hijack dismissRelatedLookupPopup to ensure change() is triggered
// TODO: confirm order of script loading is guaranteed?
window.djangoDismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
window.dismissRelatedLookupPopup = function(win, newId, newRepr){
    window.djangoDismissRelatedLookupPopup(win, newId, newRepr);
    django.jQuery("#"+windowname_to_id(win.name)).change();
}

window.djangoDismissAddAnotherPopup = window.dismissAddAnotherPopup;
window.dismissAddAnotherPopup = function(win, newId, newRepr){
    window.djangoDismissAddAnotherPopup(win, newId, newRepr);
    django.jQuery("#"+windowname_to_id(win.name)).change();
}

function dismissEditPopup(win, newId, newRepr){
    dismissRelatedLookupPopup(win, newId, newRepr);
}

(function($){
    $(document).ready(function(){
        $ = django.jQuery;
        $(".edit-link-group").each(function(){
            var id = $(this).attr('id').match(/edit-link-group_(\w+)$/)[1];
            var group = $(this);
            $("#"+id).change(function(){
                $(group).load(
                    $(group).find('.reload-link').attr('href') +
                        '?ids=' + escape($(this).val())
                );
            });
        });
    });
})(django.jQuery);

// TODO: prevent duplicate numbers being appended to M2M Raw ID field