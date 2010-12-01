Sortable inline templatetag
---------------------------

Functionality:
    Adding this templatetag to a change_form makes inline sortable

Assumptions:
    Inlines have integer order field; Inlines are sorted by the 'order' attribute by default

Usage example:
    In the change_form.html of our model which has inlines "Feature", "HomeFullWidthFeature" etc. 

    {% load admin_enhancements_includes %}

    {% block extrahead %}
        {{ block.super }}
        {% sortable_inlines "Feature" "HomeFullWidthFeature" "HomeHalfFeature" "HomeQuarterFeature" "CollectionFeature" %}
    {% endblock %}

Image preview
-------------

TODO: documentation


Backward incompatible changes
-----------------------------

01/12/2010:

The syntax used to be {% sortable_inlines "Image" %}.
It is now {% sortable_inlines "image_set" %}.

If you used multiple inlines:
{% sortable_inlines "Image","Video" %} now is {% sortable_inlines "image_set" "video_set" %}
