# fullstack_developer_capstone

**Project name:** `fullstack_developer_capstone`  
**Repository:** `xrwvm-fullstack_developer_capstone`

IBM Full-Stack Development Capstone: Cars Dealership Review Portal. This is a fork of the [IBM Skills Network starter](https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone). The application lets users browse U.S. dealerships, filter by state, view reviews, register, sign in, and post reviews.

## Components

- Django and SQLite application server
- React frontend
- Express and MongoDB dealership service
- Flask sentiment analysis service

## Run locally

```bash
python -m pip install -r server/requirements.txt
cd server/frontend && npm ci && npm run build && cd ../..
cd server
python manage.py migrate
python manage.py shell -c "from djangoapp.populate import initiate; initiate()"
python manage.py runserver
```

The application opens at `http://127.0.0.1:8000/`. It serves the built React app on `/register`, `/login`, `/dealers`, `/dealer/<id>`, and `/postreview/<id>`. The Home, About, and Contact pages are Django templates. The dealership API uses bundled sample data when the Express service is unavailable, so browsing works without MongoDB. New reviews are stored in SQLite.

Optional Express API: run `npm install && node app.js` from `server/database`. It uses bundled JSON data by default, or MongoDB when `MONGODB_URL` is set. Optional sentiment API: install `server/djangoapp/microservices/requirements.txt` and run `python app.py` from that directory. The bundled VADER lexicon allows offline sentiment analysis.

## Verify

```bash
cd server
python manage.py check
python manage.py test djangoapp
cd frontend && npm ci && npm run build
```

The GitHub Actions workflow runs these checks on pushes and pull requests.

## Deployment configuration

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` for the deployed host. Build React, run migrations, and collect static files before starting Django with Gunicorn. The optional `backend_url` and `sentiment_analyzer_url` variables point Django to the Express and Flask services. Do not use the development secret key in a public deployment.

A root `Dockerfile` builds React, collects static files, migrates SQLite, seeds sample cars, and starts Gunicorn. A persistent database should replace SQLite for a long-lived deployment.

For a free demo deployment, create a Render Blueprint from this repository's `render.yaml`. The Blueprint builds the root Dockerfile, generates `DJANGO_SECRET_KEY`, and sets `DJANGO_DEBUG=0`. Render supplies `RENDER_EXTERNAL_HOSTNAME`, which Django adds to its allowed hosts and trusted CSRF origins. The free web service uses ephemeral SQLite storage: user accounts and new reviews can disappear after a restart or redeploy.
