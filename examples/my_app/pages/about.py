def AboutPage():
    app_cfg = CONFIG.get("app", {})
    title = app_cfg.get("title", "PyTwerk App")

    return (
        <main class="min-h-screen bg-white px-6 py-16">
            <div class="mx-auto w-[92%] max-w-5xl">
                <h1 class="text-4xl font-black text-slate-900">About {title}</h1>
                <p class="mt-4 text-slate-600">
                    This file lives in pages/ as an additional route-style page module.
                </p>
            </div>
        </main>
    )
