# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals


import logging

from django import template

from cms.utils.placeholder import validate_placeholder_name
from django.utils import translation


log = logging.getLogger(__name__)
register = template.Library()


class Plugin(object):
    def __init__(self, render_func, render_kwargs):
        self.render_func = render_func
        self.render_kwargs = render_kwargs

    def render(self):
        html = self.render_func(**self.render_kwargs)
        return html


@register.simple_tag(takes_context=True)
def el_pagination_placeholder(context, placeholder_slot, object_name):
    """
    Takes a django cms placeholder and generate a paginate able list of objects,
    with the added cms plugins to this placeholder.
    
    e.g.:
        {% el_pagination_placeholder "placeholder_name" "var_name" %}
    """
    log.debug("Endless placeholder for %r -> %r", placeholder_slot, object_name)
    validate_placeholder_name(placeholder_slot)

    content_renderer = context.get('cms_content_renderer')
    if not content_renderer:
        log.debug("No content renderer from context -> render nothing")
        return ""

    request = context["request"]
    current_page = request.current_page
    placeholder = current_page.placeholders.get(slot=placeholder_slot)

    language=translation.get_language()
    plugins = placeholder.get_plugins(language=language) # list of CMSPlugin instances

    object_list = [
        Plugin(
            render_func=content_renderer.render_plugin,
            render_kwargs={
                "instance": plugin,
                "context": context,
                "placeholder": placeholder,
                "editable": False
            }
        )
        for plugin in plugins
    ]
    log.debug("Add %i items to context with name %r", len(object_list), object_name)
    context[object_name] = object_list

    return ""
