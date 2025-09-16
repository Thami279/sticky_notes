from django import forms
from .models import Note, Tag

class NoteForm(forms.ModelForm):
    tags_csv = forms.CharField(required=False, help_text="Comma-separated tags")
    class Meta:
        model = Note
        fields = ["title", "content", "is_pinned"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            existing = ", ".join(t.name for t in self.instance.tags.all())
            self.fields["tags_csv"].initial = existing

    def save(self, commit=True):
        instance = super().save(commit=commit)
        tags_csv = self.cleaned_data.get("tags_csv", "")
        names = [n.strip() for n in tags_csv.split(",") if n.strip()]
        tag_objs = []
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tag_objs.append(tag)
        if commit:
            instance.tags.set(tag_objs)
        else:
            # Defer setting tags until after caller saves instance
            self._pending_tags = tag_objs
        return instance
