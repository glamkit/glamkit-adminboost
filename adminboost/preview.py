from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.admin.options import InlineModelAdmin
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.encoding import force_unicode



# Admin classes ------------------------------------------------------------


class PreviewInline(InlineModelAdmin):
    def __init__(self, *args, **kwargs):
        # enforce use of fieldsets so we can inject the preview field
        if not self.fieldsets:
            self.__class__.fieldsets = (
                (None, {'fields': self.form.base_fields}),)
        super(PreviewInline, self).__init__(*args, **kwargs)
        # inject 'preview' after super init since it won't validate
        self.declared_fieldsets[0][1]['fields'] = ('preview',) + \
            tuple(self.declared_fieldsets[0][1]['fields'])    

class PreviewStackedInline(PreviewInline):
    template = 'admin/edit_inline/stacked.html'

class PreviewTabularInline(PreviewInline):
    template = 'admin/edit_inline/tabular.html'

# Form classes ------------------------------------------------------------
    
class PreviewWidget(forms.widgets.Input):
    is_hidden = False
    input_type = 'text'
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.form = kwargs.pop('form', None)
        super(PreviewWidget, self).__init__(*args, **kwargs)

class ImagePreviewWidget(PreviewWidget):        
        
    def render(self, name, data, attrs={}):
        from easy_thumbnails.files import get_thumbnailer
        from easy_thumbnails.files import Thumbnailer
        if not self.form.preview_instance_required or self.instance is not None:
            images = self.form.get_images(self.instance)
            options = dict(size=(120, 120), crop=False)
            html = '<div class="adminboost-preview">'
            for image in images:
                thumbnail = get_thumbnailer(image.file).get_thumbnail(options)
                if isinstance(image.file, Thumbnailer):
                    image_url = default_storage.url(force_unicode(image.file.name))
                else:
                    image_url = image.file.url
                html += '<div class="adminboost-preview-thumbnail"><a href="%(image_url)s" target="_blank"><img src="%(thumbnail_url)s"/></a></div>' % {'image_url': image_url, 'thumbnail_url': thumbnail.url}
            html += '</div>'
            return mark_safe(html)
        else:
            return ''
        
class PreviewField(forms.Field):
    """ Dummy "field" to provide preview thumbnail. """
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.form = kwargs.pop('form', None)
        kwargs['widget'] = self.form.preview_widget_class(instance=self.instance, form=self.form)
        super(PreviewField, self).__init__(*args, **kwargs)

class PreviewInlineForm(forms.ModelForm):
    
    preview_instance_required = True # If True, the widget will only be displayed if an instance of the model exists (i.e. the object has already been saved at least once)
    
    def __init__(self, *args, **kwargs):
        super(PreviewInlineForm, self).__init__(*args, **kwargs)
        preview_field = PreviewField(
            label = _('Preview'), required=False,
            instance = kwargs.get('instance', None), form=self)
        self.fields.insert(0, 'preview', preview_field)
        self.base_fields.insert(0, 'preview', preview_field)
        
    class Media:
        css = { 
            'all': ("%sadminboost/styles.css" % settings.MEDIA_URL,)
            }
    
class ImagePreviewInlineForm(PreviewInlineForm):
    
    preview_widget_class = ImagePreviewWidget
    
    def get_images(self, instance):
        ''' This needs to be specified by the child form class, as we cannot anticipate the name of the image model field '''
        raise NotImplementedError
