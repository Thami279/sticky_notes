from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Note, Tag
from .forms import NoteForm
from rest_framework import viewsets, permissions
from .serializers import NoteSerializer, TagSerializer
import csv
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

def signup(request):
    if request.user.is_authenticated:
        return redirect("note_list")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(request, "Account created successfully")
        return redirect("note_list")
    return render(request, "signup.html", { "form": form })


@login_required
def note_list(request):
    q = request.GET.get("q", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    qs = Note.objects.filter(user=request.user)
    if q:
        qs = qs.filter(title__icontains=q)
    active_tag = None
    if tag_slug:
        active_tag = Tag.objects.filter(slug=tag_slug).first()
        if active_tag:
            qs = qs.filter(tags=active_tag)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    notes = page_obj.object_list
    context = {
        "notes": notes,
        "q": q,
        "page_obj": page_obj,
        "paginator": paginator,
        "active_tag": active_tag,
        "all_tags": Tag.objects.all().order_by("name"),
    }
    return render(request, "note_list.html", context)

@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, "note_detail.html", {"note": note})

@login_required
def export_notes_csv(request):
    qs = Note.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="notes.csv"'
    writer = csv.writer(response)
    writer.writerow(["title", "content", "is_pinned", "tags"])  # tags as comma-separated
    for n in qs:
        tags = ",".join(n.tags.values_list("name", flat=True))
        writer.writerow([n.title, n.content, n.is_pinned, tags])
    return response

@login_required
def import_notes_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        decoded = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        count = 0
        for row in reader:
            note = Note.objects.create(
                user=request.user,
                title=row.get('title',''),
                content=row.get('content',''),
                is_pinned=row.get('is_pinned','').lower() in ('1','true','yes')
            )
            tag_names = [n.strip() for n in row.get('tags','').split(',') if n.strip()]
            if tag_names:
                tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
                note.tags.set(tags)
            count += 1
        messages.success(request, f"Imported {count} notes")
        return redirect('note_list')
    return render(request, 'import_form.html')


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Note):
            return obj.user == request.user
        return True


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = Note.objects.filter(user=self.request.user)
        q = self.request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(title__icontains=q)
        tag = self.request.query_params.get("tag", "").strip()
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs

    def perform_create(self, serializer):
        serializer.save()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.all().order_by("name")

@login_required
def note_create(request):
    form = NoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.user = request.user
        note.save()
        messages.success(request, "Note created")
        return redirect("note_detail", pk=note.pk)
    return render(request, "note_form.html", {"form": form})

@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    form = NoteForm(request.POST or None, instance=note)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Note updated")
        return redirect("note_detail", pk=note.pk)
    return render(request, "note_form.html", {"form": form})

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted")
        return redirect("note_list")
    return render(request, "note_detail.html", {"note": note})
