from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


class NoteModelTests(TestCase):
    def test_str(self):
        user = User.objects.create_user(username="u", password="p")
        note = Note.objects.create(user=user, title="T", content="C")
        self.assertEqual(str(note), "T")

    def test_ordering_pinned_first_then_updated(self):
        user = User.objects.create_user(username="u2", password="p")
        a = Note.objects.create(user=user, title="A", content="", is_pinned=False)
        b = Note.objects.create(user=user, title="B", content="", is_pinned=True)
        self.assertEqual(list(Note.objects.filter(user=user)), [b, a])


class NoteViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", password="pass")
        self.user2 = User.objects.create_user(username="bob", password="pass")

    def test_login_required(self):
        resp = self.client.get(reverse("note_list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_only_own_notes_listed(self):
        Note.objects.create(user=self.user1, title="mine", content="")
        Note.objects.create(user=self.user2, title="theirs", content="")
        self.client.login(username="alice", password="pass")
        resp = self.client.get(reverse("note_list"))
        self.assertContains(resp, "mine")
        self.assertNotContains(resp, "theirs")

    def test_create_sets_user(self):
        self.client.login(username="alice", password="pass")
        resp = self.client.post(reverse("note_create"), {"title": "T", "content": "C", "is_pinned": True})
        self.assertEqual(resp.status_code, 302)
        note = Note.objects.get()
        self.assertEqual(note.user, self.user1)
        self.assertTrue(note.is_pinned)

    def test_detail_requires_ownership(self):
        note = Note.objects.create(user=self.user2, title="B", content="")
        self.client.login(username="alice", password="pass")
        resp = self.client.get(reverse("note_detail", args=[note.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_update_and_delete(self):
        note = Note.objects.create(user=self.user1, title="A", content="")
        self.client.login(username="alice", password="pass")
        resp = self.client.post(reverse("note_update", args=[note.pk]), {"title": "A2", "content": "X", "is_pinned": False})
        self.assertEqual(resp.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, "A2")
        resp = self.client.post(reverse("note_delete", args=[note.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())

