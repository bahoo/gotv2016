from django import forms
from .models import PrecinctCoordinator


class PrecinctCoordinatorForm(forms.ModelForm):
    pass

    class Meta:
        model = PrecinctCoordinator
        exclude = []