from django.db.models import ImageField

from .settings import ADMINBOOST_PREVIEW_SIZE
from .widgets import PreviewImageWidget


class PreviewImageField(ImageField):
    """
    A subclass of ImageField that renders along with a preview thumbnail in
    the admin, Takes an optional "preview_size" argument (consisting of a
    (width, height) tuple) on initialisation that determines the dimensions of
    the preview. If one isn't provided the value of the ADMINBOOST_PREVIEW_SIZE
    setting is used. To change the displayed preview more fundamentally,
    override "adminboost/_preview_image.htnl".
    """
    
    def __init__(self, *args, **kwargs):
        self.preview_size = kwargs.pop('preview_size', ADMINBOOST_PREVIEW_SIZE)
        super(PreviewImageField, self).__init__(*args, **kwargs)
    
    def formfield(self, *args, **kwargs):
        kwargs['widget'] = PreviewImageWidget(preview_size=self.preview_size)
        return super(PreviewImageField, self).formfield(*args, **kwargs)
    
    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.files.ImageField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
