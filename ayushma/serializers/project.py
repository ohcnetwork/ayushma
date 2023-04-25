from rest_framework import serializers

from ayushma.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("external_id", "title", "created_at", "modified_at", "description")
        read_only_fields = ("external_id", "created_at", "modified_at")
