from django.forms import modelformset_factory
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import PrecinctCoordinatorForm
from .models import PrecinctCoordinator



class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context['formset'] = modelformset_factory(PrecinctCoordinator, fields=['full_name'])
        return context