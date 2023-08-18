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
    

