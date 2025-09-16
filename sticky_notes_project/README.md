# Sticky Notes

This is a Django-based sticky notes app.

## Signup and Authentication
- Visit `/accounts/signup/` to create an account.
- After signup, you are redirected to your notes list.
- Use `/accounts/login/` to log in and `/accounts/logout/` to log out.

## Running locally
```bash
python3 sticky_notes_project/manage.py migrate
python3 sticky_notes_project/manage.py runserver
```

## Deployment
This repo is ready for platforms like Render or Railway.
- Set `ALLOWED_HOSTS` to your domain or `['*']` for testing in `sticky_notes_project/sticky_notes_project/settings.py`.
- Ensure `DEBUG=False` for production.
- Configure a production database and `SECRET_KEY` via environment variables.

## API Endpoints
- `GET /api/notes/` - list authenticated user notes
- `GET /api/tags/` - list tags
