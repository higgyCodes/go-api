from rest_framework import serializers
from .models import (
    ERUOwner,
    ERU,
    PersonnelDeployment,
    Personnel,
    Heop,
    Fact,
    FactPerson,
    Rdrt,
    RdrtPerson,
    PartnerSocietyActivities,
    PartnerSocietyDeployment,
    RegionalProject,
    Project,
)
from api.serializers import (
    ListEventSerializer,
    MiniCountrySerializer,
    MiniDistrictSerializer,
)

class ERUSetSerializer(serializers.ModelSerializer):
    deployed_to = MiniCountrySerializer()
    class Meta:
        model = ERU
        fields = ('type', 'units', 'equipment_units', 'deployed_to', 'event', 'eru_owner', 'available', 'id',)

class ERUOwnerSerializer(serializers.ModelSerializer):
    eru_set = ERUSetSerializer(many=True)
    national_society_country = MiniCountrySerializer()
    class Meta:
        model = ERUOwner
        fields = ('created_at', 'updated_at', 'national_society_country', 'eru_set', 'id',)

class ERUSerializer(serializers.ModelSerializer):
    deployed_to = MiniCountrySerializer()
    event = ListEventSerializer()
    eru_owner = ERUOwnerSerializer()
    class Meta:
        model = ERU
        fields = ('type', 'units', 'equipment_units', 'deployed_to', 'event', 'eru_owner', 'available', 'id',)

class PersonnelDeploymentSerializer(serializers.ModelSerializer):
    country_deployed_to = MiniCountrySerializer()
    event_deployed_to = ListEventSerializer()
    class Meta:
        model = PersonnelDeployment
        fields = ('country_deployed_to', 'region_deployed_to', 'event_deployed_to', 'comments', 'id',)

class PersonnelSerializer(serializers.ModelSerializer):
    country_from = MiniCountrySerializer()
    deployment = PersonnelDeploymentSerializer()
    class Meta:
        model = Personnel
        fields = ('start_date', 'end_date', 'name', 'role', 'type', 'country_from', 'deployment', 'id',)

class PartnerDeploymentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerSocietyActivities
        fields = ('activity', 'id',)

class PartnerDeploymentSerializer(serializers.ModelSerializer):
    parent_society = MiniCountrySerializer()
    country_deployed_to = MiniCountrySerializer()
    district_deployed_to = MiniDistrictSerializer(many=True)
    activity = PartnerDeploymentActivitySerializer()
    class Meta:
        model = PartnerSocietyDeployment
        fields = ('start_date', 'end_date', 'name', 'role', 'parent_society', 'country_deployed_to', 'district_deployed_to', 'activity', 'id',)


class RegionalProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionalProject
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    project_district_detail = MiniDistrictSerializer(source='project_district', read_only=True)
    reporting_ns_detail = MiniCountrySerializer(source='reporting_ns', read_only=True)
    regional_project_detail = RegionalProjectSerializer(source='regional_project', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            field: {
                'allow_null': False, 'required': True,
            } for field in ['user', 'reporting_ns', 'project_district', 'name']
        }

