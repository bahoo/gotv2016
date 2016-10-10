from django import forms
from django.contrib.admin import widgets
from django.contrib import admin
from django.contrib.gis import admin as geo_admin
from django.db import models
from django.utils.html import mark_safe
import json
import urllib

from localflavor.us.models import PhoneNumberField

from .models import Area, PrecinctCoordinator, WaPrecinct
from .widgets import ForeignKeyRawIdHiddenWidget


@admin.register(WaPrecinct)
class WaPrecinctAdmin(geo_admin.OSMGeoAdmin):
    list_display = ['long_name', 'short_name', 'county']
    search_fields = ['long_name']

    def get_queryset(self, request):
        return super(WaPrecinctAdmin, self).get_queryset(request).defer('map_cache_geometry') 


class PrecinctStatusListFilter(admin.SimpleListFilter):
    title = "Precinct Status"
    parameter_name = 'precinct_status'

    def lookups(self, request, model_admin):
        return (
            ('needs-walker', "Needs Walker"),
            ('needs-packets', "Has Walker, Needs Packets"),
            ('needs-walk', "Has Packet, Needs to Walk"),
            ('needs-enter-data', "Has Walked, Needs to Enter Data"),
            ('done', "Done!")
        )

    def queryset(self, request, queryset):
        lookup_to_status = {
            'needs-walker': {'status': 'will-walk'},
            'needs-packets': {'status': 'will-walk'},
            'needs-walk': {'status': 'picked-up-packet'},
            'needs-enter-data': {'status': 'walked'},
            'done': {'status': 'data-entered'}
        }

        if self.value():
            matching = queryset.filter(**lookup_to_status[self.value()])
            
            if self.value() == 'needs-walker':
                precinct_ids_to_exclude = matching.values_list('precinct_id', flat=True)
                return queryset.exclude(precinct_id__in=precinct_ids_to_exclude).exclude(status='will-not-walk')
            else:
                return matching

        return queryset


class HideMapListFilter(admin.SimpleListFilter):
    title = "Show Points and Shapes on Map"
    parameter_name = "show_map"

    def lookups(self, request, model_admin):
        return (
            (False, "No"),
        )

    def queryset(self, request, queryset):
        return queryset


@admin.register(PrecinctCoordinator)
class PrecinctCoordinatorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'precinct', 'phone_number_linebreaks', 'linkable_email', 'status']
    list_filter = ['area', PrecinctStatusListFilter, 'status', 'affiliations', HideMapListFilter]
    raw_id_fields = ['precinct']
    search_fields = ['full_name', 'email', 'phone_number', 'precinct__long_name']
    change_list_template = 'admin/areas/area/precinct-coordinator-changelist.html'
    list_select_related = ['area', 'precinct']

    def get_queryset(self, request, *args, **kwargs):
        self.request = request
        return super(PrecinctCoordinatorAdmin, self).get_queryset(request, *args, **kwargs).prefetch_related('affiliations')


    def phone_number_linebreaks(self, obj):
        return mark_safe("<br />".join(obj.phone_number.split('\n')))
    phone_number_linebreaks.short_description = "Phone Number"
    phone_number_linebreaks.admin_order_field = "phone_number"

    def linkable_email(self, obj):
        if not obj.email:
            return ''
        extra = {}
        first_name = obj.full_name.split(' ')[0]
        precinct_name = obj.precinct.long_name
        author_name = self.request.user.first_name

        if len(filter(lambda a: a.slug in ['elected', 'appointed', 'acting', 'elected-post-reorg'], obj.affiliations.all())):
            descriptor = 'PCOs'
        elif len(filter(lambda a: a.slug == 'delegate', obj.affiliations.all())):
            descriptor = 'precinct delegates who caucused with us in March,'
        else:
            descriptor = 'volunteers'

        subject_verb = "planning on" if len(filter(lambda a: a.slug == 'elected', obj.affiliations.all())) else 'interested in'

        if not obj.status:
            extra = {
                'subject': "[46 Dems] %(first_name)s, are you %(verb)s walking your precinct?" % {'first_name': first_name, 'verb': subject_verb},
                'body': """Hi %(first_name)s,

My name is %(author_name)s, I'm a volunteer with the 46th District Democrats.

Election Day is just around the corner, and we are excited to be ramping up our Get Out the Vote efforts in the 46th. We are reaching out to %(descriptor)s and wondered if you'd be interested in walking your precinct, %(precinct_name)s? It would be a huge help toward turning out Democratic voters in your neighborhood, and with your help, we will win big on Election Day.

We have got a packet with a walk list and literature all ready to go. We can also set you up with a mobile phone app called MiniVAN, which makes walking your precinct a breeze.

Let me know if you're interested, and we'll get you all setup. We'd love to have your help in making this election a big success for Democrats.

Thanks, %(first_name)s!

%(author_name)s""" % {'first_name': first_name, 'author_name': author_name, 'precinct_name': precinct_name, 'descriptor': descriptor}
            }

        elif obj.status == 'will-walk':


            ## TODO: add more location specific logic.
            extra = {
                'subject': "%(first_name)s, your walk packet for %(precinct_name)s is ready for pickup" % {'first_name': first_name, 'precinct_name': precinct_name},
                'body': """Hi %(first_name)s,

Just a friendly heads up -- your precinct walk packet is available for pickup.



Please make a plan to scoop it up and walk your precinct (and let me know if you have any questions!)

Thanks!

%(author_name)s""" % {'first_name': first_name, 'author_name': author_name}
            }


        elif obj.status == 'picked-up-packet':
            extra = {
                'subject': "How's it going?",
                'body': """Hey %(first_name)s,

Just checking in -- have you been able to walk your precinct?

Thanks!

%(author_name)s""" % {'first_name': first_name, 'author_name': author_name}
            }

        # URL encode the values, but not the keys.
        for k, v in extra.iteritems():
            extra[k] = "%0D%0A".join(v.split('\n'))

        return mark_safe("<a href=\"mailto:%(email)s%(extra)s\" target=\"_blank\">%(email)s</a>" % {'email': obj.email, 'extra': '?' +  "&".join(["=".join([k,v]) for k,v in extra.iteritems()]) if extra else ''})
    linkable_email.short_description = "Email"
    linkable_email.admin_order_field = "email"


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