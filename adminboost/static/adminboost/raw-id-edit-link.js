// duplicated from contrib.admin's RelatedObjectLookups.js

function get_edit_popup_id(edit_link){
	return django.jQuery(edit_link)
		.closest('.edit-link-group')
		.prev('a.related-lookup')
		.attr('id')
		.replace(/^lookup_/, '');
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
	django.jQuery("#lookup_"+windowname_to_id(win.name)).change();
}

window.djangoDismissAddAnotherPopup = window.dismissAddAnotherPopup;
window.dismissAddAnotherPopup = function(win, newId, newRepr){
	window.djangoDismissAddAnotherPopup(win, newId, newRepr);
	django.jQuery("#lookup_"+windowname_to_id(win.name)).change();
}

function dismissEditPopup(win, newId, newRepr){
	dismissRelatedLookupPopup(win, newId, newRepr);
}

(function($){
	$(document).ready(function(){
		$(".edit-link-group").each(function(){
			var group = $(this);
			$(this).prev('a.related-lookup').change(function(){
				$(group).load(
					$(group).find('.reload-link').attr('href') +
						'?ids=' + escape($(this).prevAll('input')[0].value)
				);
			});
		});
	});
})(django.jQuery);

// TODO: prevent duplicate numbers being appended to M2M Raw ID field