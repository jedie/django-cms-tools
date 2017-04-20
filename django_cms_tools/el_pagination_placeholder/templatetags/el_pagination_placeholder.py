# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals


import logging

from django import template

from cms.templatetags.cms_tags import Placeholder
from cms.utils.placeholder import validate_placeholder_name


log = logging.getLogger(__name__)

register = template.Library()


class Plugin(object):
    def __init__(self, render_func, render_args, render_kwargs):
        self.render_func = render_func
        self.render_kwargs = render_kwargs
        self.render_args = render_args

    def render(self):
        html = self.render_func(*self.render_args, **self.render_kwargs)
        return html


class ElPaginationContentRenderer(object):
    def __init__(self, render_plugin_func):
        self.all_plugins = []
        self.render_plugin_func = render_plugin_func

    def __call__(self, *args, **kwargs):
        self.all_plugins.append(
            Plugin(self.render_plugin_func, args, kwargs)
        )
        # Don't put the generated html code into the page, yet.
        return ""


class ElPaginationPlaceholder(Placeholder):
    """
    Takes a django cms placeholder and generate a paginate able list of objects,
    with the added cms plugins to this placeholder.
    
    FIXME: Currently we do this by a hack: We change the method:
        cms.plugin_rendering.ContentRenderer().render_plugin()
    to get all plugins.
    
    usage e.g.:
        {% el_pagination_placeholder "placeholder_name" %}
    """
    def render_tag(self, context, name, extra_bits, nodelist=None):
        validate_placeholder_name(name)

        content_renderer = context.get('cms_content_renderer')
        # content_renderer == cms.plugin_rendering.ContentRenderer() instance

        if not content_renderer:
            log.debug("No content renderer from context -> render nothing")
            return ''

        # Overwrite the plugin render method to catch all placeholder plugins
        el_pagination_renderer = ElPaginationContentRenderer(content_renderer.render_plugin)
        content_renderer.render_plugin = el_pagination_renderer

        super(ElPaginationPlaceholder, self).render_tag(context, name, extra_bits, nodelist=nodelist)

        all_plugins = el_pagination_renderer.all_plugins
        context["all_plugins"] = all_plugins

        log.debug("Add %i items to context['all_plugins']", len(all_plugins))
        return ""


register.tag("el_pagination_placeholder", ElPaginationPlaceholder)
