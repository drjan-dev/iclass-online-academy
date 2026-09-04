# iClass Online Academy — Django Website


A real, working Django site for iClass Online Academy: track selection (WAEC/NECO,
JAMB, Cambridge IGCSE, Cambridge A-Levels, IJMB), subject resources (lesson
slides, videos, textbooks, Padlet), tutor booking, and a full test engine
(individual subject tests, topic-based tests, and the full JAMB Combo Test with
a live countdown timer, auto-submit, and scored results with feedback).

## 1. Run it on your computer (Windows)

**You need Python installed first.** If you haven't already:
1. Download it from https://python.org/downloads
2. During install, tick **"Add python.exe to PATH"**

**Then, in Command Prompt (search "cmd" in the Start menu):**

```
cd path\to\this\folder
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_iclass
python manage.py createsuperuser
python manage.py runserver
```

- `venv\Scripts\activate` activates a clean, isolated Python environment for this
  project only — you'll see `(venv)` appear in your terminal prompt.
- `seed_iclass` fills the database with the 5 tracks, 5 subjects, and sample
  questions so the site isn't empty.
- `createsuperuser` creates your admin login — it'll ask for a username, email,
  and password.
- `runserver` starts the site. Open **http://127.0.0.1:8000/** in your browser.
- Manage all content (add real questions, resources, tutors) at
  **http://127.0.0.1:8000/admin/** using the superuser login you just created.

To stop the server, press `Ctrl+C` in the terminal. To come back to it later,
you only need `venv\Scripts\activate` then `python manage.py runserver` — no
need to reinstall anything.

## 2. Add your real content

The seed command only adds a handful of sample questions per subject so you
can see the test engine working. Add your real question banks, lesson
resources, and tutors through the admin panel at `/admin/` — no coding needed
for that part.

## 3. Deploy it live on the internet

This project is deployment-ready (it uses environment variables for the
secret key and allowed hosts, and Whitenoise to serve static files in
production). Recommended beginner-friendly hosts: **Railway** or **Render**
(both have free/cheap tiers).

General steps (host-specific instructions will vary slightly):
1. Push this project to a GitHub repository.
2. Create an account on Railway or Render and connect your GitHub repo.
3. Set these environment variables on the host:
   - `DJANGO_SECRET_KEY` — any long random string
   - `DJANGO_DEBUG` — `False`
   - `DJANGO_ALLOWED_HOSTS` — your host's domain (e.g. `iclass.up.railway.app`)
4. The host will run `pip install -r requirements.txt` automatically, then
   start the app using the included `Procfile`.
5. Run `python manage.py migrate` and `python manage.py seed_iclass` once,
   using the host's console/shell feature.
6. Visit your live URL — the site is now on the internet.

A custom domain (e.g. `iclassacademy.com`) is optional and can be pointed at
your host afterward for a small yearly fee.

## Project structure

```
iclass_project/   → Django project settings, root URLs
academy/          → The app: models, views, templates, admin, seed command
static/css/       → Site stylesheet (navy/parchment/gold identity)
requirements.txt  → Python packages needed
Procfile          → Tells hosting platforms how to start the site
```
