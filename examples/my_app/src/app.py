def App(content: object):
    app_cfg = CONFIG.get("app", {})
    title = app_cfg.get("title", "PyTwerk App")

    return (
        <main class="min-h-screen bg-slate-100">
            <section class="px-6 pt-10 pb-4">
                <div class="mx-auto w-[92%] max-w-5xl">
                    <p class="text-xs uppercase tracking-[0.16em] text-slate-500">PyTwerk Layout</p>
                    <p class="mt-2 text-slate-700">App shell for {title}</p>
                </div>
            </section>
            {raw_html(str(content))}
        </main>
    )
