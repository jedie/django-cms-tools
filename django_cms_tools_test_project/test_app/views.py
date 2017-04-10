# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals


from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "index_view.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["content"] = "Hello World!"
        return context
