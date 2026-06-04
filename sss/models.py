from django.contrib import auth
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

UserModel = auth.get_user_model()

private_storage = FileSystemStorage(
    location=settings.PRIVATE_MEDIA_STORAGE_LOCATION,
    base_url=settings.PRIVATE_MEDIA_BASE_URL,
)


def legend_upload_path(instance, filename):
    return os.path.join("legend_files", filename)



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
    browser_expiry = models.IntegerField(null=True,blank=True,default=None)
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


class ManagementCommandStatus(models.Model):

    command = models.CharField(max_length=255, null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = 'sss'
        verbose_name = "Management Command Status"
        verbose_name_plural = "Management Command Status"
        ordering = ['-completion_time']

    def __str__(self):
        return self.command


class MapServer(models.Model):                
        name = models.CharField(max_length=500, null=True, blank=True)
        url =  models.CharField(max_length=500, null=True, blank=True)
        updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
        created = models.DateTimeField(default=timezone.now)

        def __str__(self):
            return self.name     

class Proxy(models.Model):
    request_path = models.CharField(max_length=255)
    proxy_url = models.CharField(max_length=255)
    basic_auth_enabled = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        app_label = "sss"
        ordering = ["request_path"]
        verbose_name = "Proxy"
        verbose_name_plural = "Proxies"

    def save(self, *args, **kwargs):
        if self.basic_auth_enabled:
            if self.username == "" or self.password == "":
                raise ValueError("Username and password are required for basic auth")
        super().save(*args, **kwargs)


CATALOGUE_TYPE = (
    ('', "None"),
    ('TileLayer','TileLayer'),
    ('TileLayer2','TileLayer2'),
    ('TileWMSLayer','TileWMSLayer'),
    ('WMSLayer','WMSLayer'),    
    ('ImageLayer','ImageLayer'),
    ('WFSLayer','WFSLayer')
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
        service_type = models.CharField(max_length=10, null=True, blank=True, default='WMS')
        service_type_version = models.CharField(max_length=10, null=True, blank=True, default='1.1.1')
        legend = models.FileField(storage=private_storage, upload_to=legend_upload_path, null=True, blank=True)
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
        
class SpatialDataCalculation(models.Model):
    CALCULATION_STATUS = (
    ('Imported', 'Imported'),
    ('Calculating', 'Calculating'),
    ('Processing Finalised', 'Processing Finalised'),
    ('Calculation Error', 'Calculation Error'),
    ('Completed', "Completed"),
    ('Failed', 'Failed')
)
    bfrs = models.CharField(max_length=500)
    calculation_status = models.CharField('Calculation Status', 
        max_length=40, choices=CALCULATION_STATUS,
        default=CALCULATION_STATUS[0][0])
    features = models.TextField(null=True, blank=True)
    options = models.TextField(null=True, blank=True)
    tasks = models.TextField(null=True, blank=True)
    spatial_data = models.TextField(null=True, blank=True)
    output = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    error = models.TextField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    logs = models.TextField(default='',null=True, blank=True)

class CRSSettings(models.Model):
    CRS_CHOICES = [
        ("EPSG:3577", "GDA94 / Australian Albers"),
        ("EPSG:9473", "GDA2020 / Australian Albers"),
    ]

    crs = models.CharField(
        max_length=10,
        choices=CRS_CHOICES,
        default="EPSG:3577",  # Default to GDA94 / Australian Albers
    )

    class Meta:
        verbose_name = "CRS Setting"
        verbose_name_plural = "CRS Setting"
        
    def __str__(self):
        return dict(self.CRS_CHOICES)[self.crs]

class AccessGroup(models.Model):
    group_name = models.CharField(max_length=255, unique=True)
    access_list = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.group_name