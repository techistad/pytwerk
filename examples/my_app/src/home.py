from src.app import App
from src.components import About, HeroSection


def Home():
    app_cfg = CONFIG.get("app", {})
    links = CONFIG.get("external_links", [])
    title = app_cfg.get("title", "PyTwerk App")
    content = f"{HeroSection(title=title)}{About(links=links)}"
    return App(raw_html(content))
