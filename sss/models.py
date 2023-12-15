from django.contrib import auth
from django.db import models
from django.core.cache import cache
from django.utils import timezone

UserModel = auth.get_user_model()

DISTRICT_CHOICES = (
    ('PHS', "Perth Hills"),
    ('SWC', "Swan Coastal"),
    ('BWD', "Blackwood"),
    ('WTN', "Wellington"),
    ('DON', "Donnelly"),
    ('FRK', "Frankland"),
    ('ALB', "Albany"),
    ('ESP', "Esperance"),
    ('EKM', "East Kimberley"),
    ('WKM', "West Kimberley"),
    ('EXM', "Exmouth"),
    ('PIL', "Pilbara"),
    ('KAL', "Kalgoorlie"),
    ('GER', "Geraldton"),
    ('MOR', "Moora"),
    ('SHB', "Shark Bay"),
    ('GSN', "Great Southern"),
    ('CWB', "Central Wheatbelt"),
    ('SWB', "Southern Wheatbelt")
)

REGION_CHOICES = (
    ('kimberley','Kimberley'),
    ('pilbara','Pilbara'),
    ('midwest','Midwest'),
    ('goldfields','Goldfields'),
    ('swan','Swan'),
    ('wheatbelt','Wheatbelt'),
    ('south west','South West'),
    ('warren','Warren'),
    ('south coast','South Coast')
)
class Region(models.Model):
    name = models.CharField(choices=REGION_CHOICES, unique=True, default=None, max_length=64)

    class Meta:
        app_label = 'sss'
        
    def __str__(self):
        return f"{self.name}"


class District(models.Model):
    name = models.CharField(choices=DISTRICT_CHOICES, unique=True, max_length=64)
    region = models.ForeignKey(Region, on_delete=models.CASCADE )

    class Meta:
        app_label = 'sss'

    def __str__(self):
        return f"{self.name}"

class UserProfile(models.Model):
    user = models.ForeignKey(
        UserModel,
        default=None,
        blank=True,
        null=True,
        related_name="user",
        on_delete=models.SET_NULL,
    )
    region = models.ForeignKey(Region, default=None, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, default=None, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'sss'

    def __str__(self):
        return f"{self.user}"
    
class ProxyCache(models.Model):
    layer_name = models.CharField(max_length=500)
    cache_expiry = models.IntegerField(default=300)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'sss'

    def __str__(self):
        return f"{self.layer_name}"
    
    def save(self, *args, **kwargs):
        cache.delete('utils_cache.get_proxy_cache()')
        self.full_clean()
        super(ProxyCache, self).save(*args, **kwargs)
    

class BomSyncList(models.Model):
        file_name = models.CharField(max_length=500)
        active = models.BooleanField(default=True)
        created = models.DateTimeField(default=timezone.now)

        class Meta:
            app_label = 'sss'

        def __str__(self):
            return f"{self.file_name}"


class MapServer(models.Model):                
        name = models.CharField(max_length=500, null=True, blank=True)
        url =  models.CharField(max_length=500, null=True, blank=True)
        updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
        created = models.DateTimeField(default=timezone.now)

        def __str__(self):
            return self.name     
        
CATALOGUE_TYPE = (
    ('', "None"),
    ('TileLayer','TileLayer'),
    ('TileLayer2','TileLayer2'),
    ('TileWMSLayer','TileWMSLayer'),
    ('WMSLayer','WMSLayer'),    
    ('ImageLayer','ImageLayer')
)
class Catalogue(models.Model):
        title =  models.CharField(max_length=500, null=True, blank=True)
        identifier = models.CharField(max_length=500)
        map_server = models.ForeignKey(MapServer, default=None, on_delete=models.SET_NULL, null=True, blank=True)
        #type =  models.CharField(max_length=500, null=True, blank=True, help_text="Map Server Type TileLayer, ImageLayer, WMSLayer etc")                  
        type = models.CharField(choices=CATALOGUE_TYPE, default='', null=True, blank=True, max_length=128, help_text="Map Server Type TileLayer, ImageLayer, WMSLayer etc")
        workspace = models.CharField(max_length=500, null=True, blank=True)
        url = models.CharField(max_length=500, null=True, blank=True)        
        any_text = models.TextField(null=True, blank=True)
        abstract = models.TextField(null=True, blank=True)
        keywords = models.CharField(max_length=500, null=True, blank=True)
        bounding_box = models.TextField(null=True, blank=True, help_text="Maps to pycsw:BoundingBox. It's a WKT geometry")
        crs = models.CharField(max_length=255, null=True, blank=True, help_text='Maps to pycsw:CRS')
        service_type = models.CharField(max_length=10, null=True, blank=True)
        service_type_version = models.CharField(max_length=10, null=True, blank=True)
        legend = models.CharField(max_length=500, null=True, blank=True)
        active = models.BooleanField(default=True)
        updated = models.DateTimeField(auto_now_add=True)
        created = models.DateTimeField(default=timezone.now)

class CatalogueTag(models.Model):
                                
        catalogue = models.ForeignKey(Catalogue, default=None, on_delete=models.CASCADE, null=True, blank=True)                
        name = models.CharField(max_length=500)
        description = models.CharField(max_length=500, null=True, blank=True)

        def __str__(self):
            return self.name         


class CatalogueSyncCSW(models.Model):
        
        csw_id = models.IntegerField(null=True, blank=True)
        identifier = models.CharField(max_length=500)
        json_data = models.TextField(null=True, blank=True)
        active = models.BooleanField(default=True)
        removed_from_csw = models.BooleanField(default=False)
        updated = models.DateTimeField(auto_now_add=True)
        created = models.DateTimeField(default=timezone.now)        

        def __str__(self):
            return self.identifier          