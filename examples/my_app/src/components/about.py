@component
def About(links: list[dict[str, str]] | None = None):
    safe_links = links or []
    rendered_links = []
    for item in safe_links:
        label = text(item.get("label", "Link"))
        href = text(item.get("href", "#"))
        rendered_links.append(
            f'<a class="underline decoration-slate-400 hover:decoration-slate-900" href="{href}" target="_blank" rel="noreferrer">{label}</a>'
        )
    links_html = " | ".join(rendered_links) if rendered_links else ""

    return (
        <section class="px-6 pb-16">
            <div class="mx-auto w-[92%] max-w-5xl bg-white rounded-2xl p-8 border border-slate-200">
                <h2 class="text-2xl font-bold text-slate-900">About This Starter</h2>
                <p class="mt-3 text-slate-600">
                    Build components in src/components and compose root content in src/home.py.
                </p>
                <p class="mt-4 text-sm text-slate-600">{raw_html(links_html)}</p>
            </div>
        </section>
    )
