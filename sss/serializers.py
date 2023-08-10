from rest_framework import serializers
from sss.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    district = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ( 'district',
                    'district_id',
                    'region',
                    'region_id',
                    'user_id',
                    'username'
                )

    def get_district(self,obj):
        if obj.district:
            return obj.district.name
        
    
    def get_region(self,obj):
        if obj.region:
            return obj.region.name
        
    def get_username(self,obj):
        if obj.user:
            if obj.user.email:
                username, domain = obj.user.email.split("@")
                domain_name = domain.split(".")[0]
                return f"{username}.{domain_name}"
            
class AccountDetailsSerializer(serializers.ModelSerializer):
    authenticated = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (  'authenticated',
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'full_name',
                    'groups'
                )

    def get_authenticated(self,obj):
        if obj.user:
            return obj.user.is_authenticated
    
    def get_email(self,obj):
        if obj.user:
            return obj.user.email
        
    def get_username(self,obj):
        if obj.user:
            return obj.user.username

    def get_first_name(self,obj):
        if obj.user:
            return obj.user.first_name

    def get_last_name(self,obj):
        if obj.user:
            return obj.user.last_name

    def get_full_name(self,obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"

    def get_groups(self,obj):
        if obj.user:
            group_names = ",".join(obj.user.groups.values_list('name', flat=True))
            return group_names
        