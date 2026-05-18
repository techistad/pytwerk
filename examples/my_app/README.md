# My App

Scaffolded with PyTwerk CLI.

## Structure

- `src/` app composition (`app.py`, `home.py`) + components + styles
- `pages/` additional page modules (`about.py`, `blog.py`, etc.)
- `public/` static assets
- `twerk.config.py` project configuration (Next/Vite style)

Engine note: inside PyTwerk-loaded files, `component`, `text`, `raw_html`, and
`import_component`, `load_twerk_config` are available automatically.

## Run

```bash
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

## API

- `GET /api/health`
- `GET /api/meta`
