from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import (
    ManyToManyRawIdWidget, ForeignKeyRawIdWidget)
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe

def _template_list(obj, template_name):
    return (
        'adminboost/%s/%s/%s' % (
            obj._meta.app_label, obj._meta.object_name.lower(), template_name),
        'adminboost/%s/%s' % (obj._meta.app_label, template_name),
        'adminboost/%s' % template_name,
        )

def render_edit_link(obj, db_field, popup=True, request=None):
    change_permission = '%s.change_%s' % (
        obj._meta.app_label, obj._meta.object_name.lower())
    if request and not request.user.has_perm(change_permission, obj):
        return u'<strong>%s</strong>' % escape(smart_unicode(obj))
    try:
        change_url = reverse(
            "admin:%s_%s_change" % (
                obj._meta.app_label, obj._meta.object_name.lower()),
            args=(obj.pk,))
    except NoReverseMatch:
        change_url = '#error:no-change-form'
    input_id = 'id_%s' % db_field.name
    # (TODO: Use actual id prefix if custom -- pass form in via widget init)
    return render_to_string(
        _template_list(obj, '_edit_popup_link.html'),
        {
            'change_url': change_url,
            'input_id': input_id,
            'object_string': escape(smart_unicode(obj)),
            'obj': obj,
            'popup': popup,
            })

# TODO: refactor these to this call the above; this is messy at present.
def render_edit_links(model, links, db_field):
    try:
        reload_url = reverse(
            'admin:%s_%s_render_edit_links' % (
                model._meta.app_label,
                model._meta.object_name.lower()),
            kwargs={'field_name': db_field.name})
    except NoReverseMatch:
        reload_url = '#error:no-reverse-match'
        # TODO: stop this from breaking in inlines, etc.
    return render_to_string(
        _template_list(model, '_edit_popup_link_group.html'), {
            'links': links,
            'field_id': 'id_%s' % db_field.name, # FIXME
            'reload_url': reload_url,
            })

class AlwaysRenderLabel(object):
    def render(self, name, value, attrs=None):
        output = super(AlwaysRenderLabel, self).render(
            name, value, attrs=attrs)
        if not value:
            output = mark_safe(
                u''.join(
                    [output, self.label_for_value(None)]))
        return output

class VerboseForeignKeyRawIdWidget(AlwaysRenderLabel, ForeignKeyRawIdWidget):
    class Media:
        js = ('adminboost/raw-id-edit-link.js',)

    def __init__(self, db_field):
        super(VerboseForeignKeyRawIdWidget, self).__init__(db_field.rel)
        self.db_field = db_field

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(
                self.db).get(**{key: value})
            try:
                link = render_edit_link(obj, self.db_field)
            except NoReverseMatch:
                link = u'<strong>%s</strong>' % escape(obj)
        except (ValueError, self.rel.to.DoesNotExist):
            return render_edit_links(
                self.db_field.model, [], self.db_field)
        else:
            return render_edit_links(
                self.db_field.model, [link], self.db_field)


class VerboseManyToManyRawIdWidget(AlwaysRenderLabel, ManyToManyRawIdWidget):
    def __init__(self, db_field):
        super(VerboseManyToManyRawIdWidget, self).__init__(db_field.rel)
        self.db_field = db_field

    def label_for_value(self, value):
        values = filter(bool, (value or '').split(','))
        links = []
        key = self.rel.get_related_field().name
        for v in values:
            try:
                obj = self.rel.to._default_manager.using(
                    self.db).get(**{key: v})
                try:
                    links.append(render_edit_link(obj, self.db_field))
                except NoReverseMatch:
                    links += [
                        u'<strong>%s</strong>' % escape(smart_unicode(obj))]
            except (ValueError, self.rel.to.DoesNotExist):
                links += [u'???']
        return render_edit_links(
            self.db_field.model, links, self.db_field)
