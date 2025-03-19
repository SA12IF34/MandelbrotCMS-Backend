from rest_framework.serializers import ModelSerializer
from .models import List, Mission


class ListSerializer(ModelSerializer):

    class Meta:
        model = List
        fields = '__all__'


class MissionSerializer(ModelSerializer):

    class Meta:
        model = Mission
        fields = '__all__'

