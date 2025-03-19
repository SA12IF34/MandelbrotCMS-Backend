from rest_framework.serializers import ModelSerializer
from .models import Project, Partition

class ProjectSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class PartitionSerializer(ModelSerializer):

    class Meta:
        model = Partition
        fields = '__all__'

