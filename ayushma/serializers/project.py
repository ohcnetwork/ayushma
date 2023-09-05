from rest_framework import serializers

from ayushma.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "external_id",
            "title",
            "created_at",
            "modified_at",
            "description",
            "stt_engine",
            "model",
            "is_default",
            "archived",
            "preset_questions",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")


class ProjectUpdateSerializer(serializers.ModelSerializer):
    key_set = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ProjectSerializer.Meta.fields + ("prompt", "open_ai_key", "key_set")
        extra_kwargs = {
            "open_ai_key": {"write_only": True},
        }
        read_only_fields = ("key_set",)

    def update(self, instance, validated_data):
        if validated_data.get("is_default", True):
            Project.objects.all().update(is_default=False)
        return super().update(instance, validated_data)

    def get_key_set(self, obj):
        return obj.open_ai_key is not None
