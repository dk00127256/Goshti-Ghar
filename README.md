# Goshti Ghar

Goshti Ghar is a local-first kids storytelling app for English, Hindi, and Marathi. It ships with a ready-to-play story library containing 90 unique, age-aware stories (10 per language per age group: `2-4`, `5-7`, and `8-12`). It features high-quality narration using a no-key neural voice service with local fallbacks.

## What changed

- App branding updated to `Goshti Ghar`
- Higher-quality no-key neural narration added for `English`, `Hindi`, and `Marathi`
- Story library remains multilingual, age-aware, and non-repeating
- Local persistence still uses `backend/data/stories.json`
- Audio files are still written to `media/audio`

## Local run on Mac

Use a fresh virtual environment. The checked-in `backend/venv` may contain packages built for a different CPU architecture and should not be trusted on every Mac.

### 1. Backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Notes:

- The app now prefers a no-key neural voice service for better quality.
- If that service is unavailable, Goshti Ghar falls back to local Meta MMS and then device-safe backup voices.
- Story generation can still use an API key if you want better text generation, but audio does not require `OPENAI_API_KEY`.
- Meta MMS model licenses are separate from this app. Review the model terms before commercial use.

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

If `npm start` is unstable on your Mac because of the installed Node version, you can still use:

```bash
npm run build
python3 -m http.server 3000 -d build
```

### 3. Open the app

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Useful commands

Regenerate narration for the full story library:

```bash
cd backend
./.venv/bin/python scripts/regenerate_audio_library.py
```

## Quick verification

Recommended checks after setup:

- `python3 -m compileall backend/app backend/scripts`
- `npm run build`
