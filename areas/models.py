from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from django import forms

from localflavor.us.models import PhoneNumberField


class WaPrecinct(models.Model):
    short_name = models.CharField(max_length=12, blank=True, null=True)
    long_name = models.CharField(max_length=100, blank=True)
    author_provided_id = models.CharField(max_length=60, blank=True, null=True)
    sq_miles = models.FloatField(blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    county_fips_code = models.CharField(max_length=60, blank=True, null=True)
    map_cache_geometry = models.MultiPolygonField(blank=True, null=True, srid=4326)

    class Meta:
        managed = False
        db_table = 'wa_precincts'
        verbose_name = 'Washington Precinct'

    def __unicode__(self):
        return self.long_name

    def jsonify(self):
        return self.map_cache_geometry.transform(4326, clone=True).simplify(0.0001).json

    def centroid(self):
        return self.map_cache_geometry.centroid.transform(4326, clone=True)


class Area(models.Model):
    AREA_MAPS = {
        'Ingraham': {
            'color': '#93B5C6',
            'precincts': ['SEA 46-1311','SEA 46-1400','SEA 46-1401','SEA 46-1404','SEA 46-2127','SEA 46-2128','SEA 46-2142','SEA 46-2143','SEA 46-2145','SEA 46-2152','SEA 46-2153','SEA 46-2221','SEA 46-2228','SEA 46-2359','SEA 46-2360','SEA 46-2363','SEA 46-2364','SEA 46-2366','SEA 46-2619'],
        },
        'Northgate': {
            'color': '#ADBD8A',
            'precincts': ['SEA 46-2313', 'SEA 46-2314', 'SEA 46-2324', 'SEA 46-2325', 'SEA 46-2326', 'SEA 46-2327', 'SEA 46-2338', 'SEA 46-2339', 'SEA 46-2340', 'SEA 46-2361', 'SEA 46-2367', 'SEA 46-2373', 'SEA 46-2796'],
        },
        'Olympic View': {
            'color': '#F0CF65',
            'precincts': ['SEA 46-1282', 'SEA 46-1283', 'SEA 46-1284', 'SEA 46-1285', 'SEA 46-1310', 'SEA 46-1312', 'SEA 46-1313', 'SEA 46-1314', 'SEA 46-2234', 'SEA 46-2236', 'SEA 46-2280', 'SEA 46-2282', 'SEA 46-2293', 'SEA 46-2295', 'SEA 46-2296', 'SEA 46-2297', 'SEA 46-2298', 'SEA 46-2311', 'SEA 46-2358', 'SEA 46-2379'],
        },
        'Olympic Hills': {
            'color': '#D7816A',
            'precincts': ['SEA 46-2341', 'SEA 46-2342', 'SEA 46-2343', 'SEA 46-2344', 'SEA 46-2345', 'SEA 46-2346', 'SEA 46-2347', 'SEA 46-2348', 'SEA 46-2349', 'SEA 46-2350', 'SEA 46-2351', 'SEA 46-2352', 'SEA 46-2353', 'SEA 46-2355', 'SEA 46-2369', 'SEA 46-2370', 'SEA 46-2371'],
        },
        'Jane Addams': {
            'color': '#BD4F6C',
            'precincts': ['SEA 46-2306', 'SEA 46-2307', 'SEA 46-2308', 'SEA 46-2316', 'SEA 46-2317', 'SEA 46-2318', 'SEA 46-2319', 'SEA 46-2320', 'SEA 46-2321', 'SEA 46-2322', 'SEA 46-2323', 'SEA 46-2328', 'SEA 46-2330', 'SEA 46-2332', 'SEA 46-2333', 'SEA 46-2334', 'SEA 46-2335', 'SEA 46-2336', 'SEA 46-2337', 'SEA 46-3677'],
        },
        'Wedgewood': {
            'color': '#065143',
            'precincts': ['SEA 46-2268', 'SEA 46-2269', 'SEA 46-2271', 'SEA 46-2285', 'SEA 46-2286', 'SEA 46-2289', 'SEA 46-2290', 'SEA 46-2291', 'SEA 46-2292', 'SEA 46-2299', 'SEA 46-2300', 'SEA 46-2302', 'SEA 46-2303', 'SEA 46-2303', 'SEA 46-2304', 'SEA 46-2305', 'SEA 46-2309', 'SEA 46-2310', 'SEA 46-2357', 'SEA 46-2378', 'SEA 46-2500', 'SEA 46-3687', 'SEA 46-3688'],
        },
        'Eckstein': {
            'color': '#129490',
            'precincts': ['SEA 46-2091', 'SEA 46-2092', 'SEA 46-2093', 'SEA 46-2094', 'SEA 46-2095', 'SEA 46-2096', 'SEA 46-2099', 'SEA 46-2100', 'SEA 46-2231', 'SEA 46-2240', 'SEA 46-2252', 'SEA 46-2253', 'SEA 46-2257', 'SEA 46-2260', 'SEA 46-2261', 'SEA 46-2263', 'SEA 46-2274', 'SEA 46-2275', 'SEA 46-2276', 'SEA 46-2277', 'SEA 46-2283'],
        },
        'Thornton Creek': {
            'color': '#70B77E',
            'precincts': ['SEA 46-1952', 'SEA 46-1953', 'SEA 46-1954', 'SEA 46-1961', 'SEA 46-2056', 'SEA 46-2097', 'SEA 46-2098', 'SEA 46-2243', 'SEA 46-2244', 'SEA 46-2245', 'SEA 46-2247', 'SEA 46-2249', 'SEA 46-2251', 'SEA 46-2264', 'SEA 46-2266', 'SEA 46-2267', 'SEA 46-2270', 'SEA 46-2272', 'SEA 46-2375', 'SEA 46-2377'],
        },
        'Laurelhurst': {
            'color': '#E0A890',
            'precincts': ['SEA 46-1955', 'SEA 46-1957', 'SEA 46-1959', 'SEA 46-1962', 'SEA 46-1963', 'SEA 46-1964', 'SEA 46-1965', 'SEA 46-1966', 'SEA 46-1967', 'SEA 46-1968', 'SEA 46-1969', 'SEA 46-1970', 'SEA 46-1971', 'SEA 46-1974', 'SEA 46-1977', 'SEA 46-1978', 'SEA 46-1980', 'SEA 46-2057', 'SEA 46-2090'],
        },
        'Lake Forest Park': {
            'color': '#CE1483',
            'precincts': ['LFP 46-0003', 'LFP 46-0092', 'LFP 46-0309', 'LFP 46-0397', 'LFP 46-0400', 'LFP 46-0517', 'LFP 46-0650', 'LFP 46-0652', 'LFP 46-0653', 'LFP 46-0653', 'LFP 46-0654', 'LFP 46-0655', 'LFP 46-0734', 'LFP 46-1056', 'LFP 46-1075', 'LFP 46-1089', 'LFP 46-1143', 'LFP 46-1186', 'LFP 46-1237', 'LFP 46-2439', 'LFP 46-2763', 'LFP 46-3380'],
        },
        'Kenmore': {
            'color': '#A2C868',
            'precincts': ['KMR 46-0036', 'KMR 46-0340', 'KMR 46-0473', 'KMR 46-0501', 'KMR 46-0535', 'KMR 46-0572', 'KMR 46-0573', 'KMR 46-0677', 'KMR 46-0686', 'KMR 46-0689', 'KMR 46-0695', 'KMR 46-0696', 'KMR 46-0820', 'KMR 46-1095', 'KMR 46-1147', 'KMR 46-1171', 'KMR 46-1181', 'KMR 46-2444', 'KMR 46-2462', 'KMR 46-2754', 'KMR 46-2764', 'KMR 46-2765', 'KMR 46-2771', 'KMR 46-3148', 'KMR 46-3592', 'KMR 46-3594'],
        }
    }
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    coordinator = models.ForeignKey(User, null=True, blank=True)
    color = models.CharField(max_length=64)

    def save(self, *args, **kwargs):
        if not self.color and self.name and self.name in self.AREA_MAPS:
            self.color = self.AREA_MAPS[self.name]['color']
        return super(Area, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Precinct Area'


class Affiliation(models.Model):
    label = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.label)
        super(Affiliation, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.label


STATUSES = (
        (None, '-'),
        ('email', 'Email'),
        ('voicemail', 'Voicemail'),
        ('will-walk', 'Will Walk'),
        ('picked-up-packet', 'Has Packet'),
        ('walked', 'Walked'),
        ('data-entered', 'Data Entered'),
        ('will-not-walk', 'Will Not Walk'),
    )

AFFILIATIONS = (
        (None, 'Other / No Data'),
        ('elected', 'Elected PCO, pre-reorg'),
        ('appointed', 'Appointed PCO, pre-reorg'),
        ('acting', 'Acting PCO, pre-reorg'),
        ('elected-post-reorg', 'Elected PCO, post-reorg'),
        ('delegate', 'Delegate'),
        ('volunteer', 'Volunteer'),
    )

class PrecinctCoordinator(models.Model):
    area = models.ForeignKey(Area, null=True)
    precinct = models.ForeignKey(WaPrecinct)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=1024)
    phone_number = models.CharField(null=True, blank=True, max_length=1024)
    # affiliation = models.CharField(default=None, choices=AFFILIATIONS, null=True, blank=True, max_length=32, help_text='')
    affiliations = models.ManyToManyField(Affiliation, blank=True)
    status = models.CharField(default=None, choices=STATUSES, null=True, blank=True, max_length=32)
    notes = models.TextField(null=True, blank=True)
    mini_van = models.BooleanField(default=False, verbose_name='MiniVAN')

    def __unicode__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.area:

            # look up corresponding area
            area_name = None
            for k,v in Area.AREA_MAPS.iteritems():
                if self.precinct.long_name in v['precincts']:
                    area_name = k
                    break
            
            if area_name:
                self.area = Area.objects.get(name=area_name)
        return super(PrecinctCoordinator, self).save(*args, **kwargs)


    class Meta:
        ordering = ('precinct__long_name', 'status', 'full_name')