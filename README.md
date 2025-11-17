# Spotify Releases Monitor

A full-stack FastAPI + Vue 3 service that authenticates with Spotify, stores users and tokens in PostgreSQL, and exposes endpoints for reading the current user, recent listening history, and playlist modifications. The FastAPI backend also serves the built Vue single-page application.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy 2.x, Alembic, httpx
- **Frontend:** Vue 3 + Vite, Axios
- **Database:** PostgreSQL 16
- **Auth:** Spotify Authorization Code flow + JWT session cookie
- **Containerization:** Docker Compose

## Prerequisites
- Docker + Docker Compose
- Spotify developer application with redirect URI `http://localhost:8000/auth/callback`

## Environment
Copy the `.env.example` file to `.env` and update the Spotify credentials and secrets:

```bash
cp .env.example .env
```

Key variables:
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`
- `SECRET_KEY` used to sign JWT cookies
- `DATABASE_URL` should target the `db` service (`postgresql+psycopg://app:app@db:5432/app`)

## Running with Docker Compose

```bash
docker compose up --build
```

The command will:
1. Start PostgreSQL (with data persisted in the `srm_db_data` volume)
2. Build the Vue frontend in the `web-build` service and place the output inside `/app/app/static`
3. Launch the FastAPI backend on `http://localhost:8000` serving API routes and the SPA

Visit `http://localhost:8000` to open the UI. The frontend calls the backend via the same base URL.

## Database Migrations
Alembic is configured under `backend/alembic`.

```bash
cd backend
alembic upgrade head
```

Ensure the `.env` file is available so Alembic can read `DATABASE_URL`.

## Local Development (without Docker)
1. **Backend**
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev   # or npm run build && cp -r dist/. ../backend/app/static
   ```

Update `APP_URL`, `API_URL`, and `CORS_ORIGINS` variables if you use different ports.

## API Overview
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/auth/login` | Redirects to Spotify for authentication |
| GET | `/auth/callback` | Handles Spotify callback, stores user + tokens, sets JWT cookie |
| POST | `/auth/logout` | Clears the session cookie |
| GET | `/me` | Returns the authenticated user profile |
| GET | `/spotify/recent` | Fetches recent listening history |
| POST | `/spotify/playlists/{playlist_id}/add` | Adds provided track URIs to the playlist |

All non-auth endpoints require the HTTP-only cookie created during the callback exchange.

## Frontend Features
- Login button that redirects to `/auth/login`
- Shows the signed-in Spotify user profile and avatar
- Displays recent track history (artists, albums)
- Simple form for adding track URIs to a playlist by ID

The frontend uses Axios with `withCredentials` enabled so the JWT cookie issues by FastAPI is automatically attached to API requests.
