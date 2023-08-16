from django.contrib.gis import admin
from sss import models


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    raw_id_fields = ('region',)

@admin.register(models.UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'region', 'district')

admin.site.register(models.Region)
admin.site.register(models.ProxyCache)
