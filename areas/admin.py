from django import forms
from django.contrib.admin import widgets
from django.contrib.gis import admin
from django.db import models
import json
from localflavor.us.models import PhoneNumberField
from .models import Area, PrecinctCoordinator, WaPrecinct
from .widgets import ForeignKeyRawIdHiddenWidget


@admin.register(WaPrecinct)
class WaPrecinctAdmin(admin.OSMGeoAdmin):
    list_display = ['long_name', 'short_name', 'county']
    search_fields = ['long_name']

    def get_queryset(self, request):
        return super(WaPrecinctAdmin, self).get_queryset(request).defer('map_cache_geometry') 


@admin.register(PrecinctCoordinator)
class PrecinctCoordinatorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'precinct', 'phone_number', 'email', 'affiliation', 'status']
    list_filter = ['status', 'affiliation', 'area']
    raw_id_fields = ['precinct']
    search_fields = ['full_name', 'email', 'phone_number', 'precinct__long_name']


class PrecinctCoordinatorInline(admin.TabularInline):
    model = PrecinctCoordinator
    raw_id_fields = ['precinct']
    read_only_fields = ['precinct']
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': '15'})},
        models.EmailField: {'widget': forms.TextInput(attrs={'size': '20'})},
        PhoneNumberField: {'widget': forms.TextInput(attrs={'size': '13'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': '3', 'cols': '20'})}
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            # override.
            kwargs['widget'] = ForeignKeyRawIdHiddenWidget(db_field.remote_field, self.admin_site, using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = widgets.AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = _('None') if db_field.blank else None

        if 'queryset' not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        return db_field.formfield(**kwargs)



@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PrecinctCoordinatorInline,]
    exclude = []


    def geojsonify(self, obj):
        return json.dumps({'type': 'Feature', 'properties': {}, 'geometry': json.loads(obj.transform(4326, clone=True).simplify(0.0001).json)})


    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)

        if obj:            
            precincts = []
            for pco in obj.precinctcoordinator_set.all():
                precincts.append({
                    'pco': pco,
                    'polygon': self.geojsonify(pco.precinct.map_cache_geometry),
                    'centroid': pco.precinct.map_cache_geometry.centroid.transform(4326, clone=True),
                })
            extra_context['precincts'] = precincts

        return self.changeform_view(request, object_id, form_url, extra_context)

    class Media:
        css = {
            "all": ("https://npmcdn.com/leaflet@0.7.7/dist/leaflet.css",)
        }
        js = ("https://npmcdn.com/leaflet@0.7.7/dist/leaflet.js",)