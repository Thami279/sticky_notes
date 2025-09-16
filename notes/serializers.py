from rest_framework import serializers
from .models import Note, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Note
        fields = ["id", "title", "content", "is_pinned", "created", "updated", "tags", "tag_names"]

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        user = self.context["request"].user
        note = Note.objects.create(user=user, **validated_data)
        if tag_names:
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            note.tags.set(tags)
        return note

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_names is not None:
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            instance.tags.set(tags)
        return instance

