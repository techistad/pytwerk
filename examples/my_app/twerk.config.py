CONFIG = {
    "app": {
        "name": "my_app",
        "title": "My App",
        "description": "My App built with PyTwerk",
    },
    "server": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": True,
    },
    "compiler": {
        "backend": "auto",  # auto | python | rust
        "rust_binary": "pytwerk-rs",
        "allow_rust_fallback": True,
    },
    "pages": {
        "home_route": "/",
        "home_component_file": "src/home.py",
        "home_component": "Home",
    },
    "styles": {
        "tailwind": True,
        "global_css_file": "src/styles/global.css",
    },
    "static": {
        "dir": "public",
        "url_path": "/public",
    },
    "external_links": [
        {"label": "PyTwerk", "href": "https://github.com/search?q=pytwerk"},
        {"label": "Flask Docs", "href": "https://flask.palletsprojects.com/"},
        {"label": "Django Docs", "href": "https://docs.djangoproject.com/"},
    ],
}
