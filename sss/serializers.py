from rest_framework import serializers
from sss.models import UserProfile, AccessGroup

import re
from typing import List


def _compile_patterns(access_list_text: str) -> List[re.Pattern]:
    """
    Convert an access_list string into compiled regex patterns.
    - Supports '*' as wildcard across the full email string.
    - Ignores blank lines and lines starting with '#'.
    """
    patterns: List[re.Pattern] = []
    text = access_list_text or ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        # Escape regex special chars then convert '*' to '.*'
        escaped = re.escape(line)
        regex = "^" + escaped.replace(r"\*", ".*") + "$"
        patterns.append(re.compile(regex, re.IGNORECASE))

    return patterns

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
    is_internal_dbca = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = (  'authenticated',
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'full_name',
                    'groups',
                    'is_internal_dbca',
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
        
    def get_is_internal_dbca(self,obj):
        if obj.user:
            group_name = "Internal DBCA"
            has_access = False
            try:
                access_group = AccessGroup.objects.get(group_name=group_name,active=True)
                if obj.user.email:
                    for pattern in _compile_patterns(access_group.access_list):
                        if pattern.fullmatch(obj.user.email):
                            has_access = True
                            break
                    return has_access 

            except AccessGroup.DoesNotExist:
                return False   
        return False
    


