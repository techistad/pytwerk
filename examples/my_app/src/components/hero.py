@component
def HeroSection(title: str):
    safe_title = text(title)

    return (
        <section class="px-6 pt-20 pb-10">
            <div class="mx-auto w-[92%] max-w-5xl bg-white rounded-2xl p-10 border border-slate-200 shadow-lg">
                <p class="text-sm uppercase tracking-[0.18em] text-slate-500">PyTwerk</p>
                <h1 class="mt-3 text-5xl font-black leading-tight text-slate-900">{safe_title}</h1>
                <p class="mt-4 text-slate-600 max-w-2xl">
                    App-level component composition, React style, but with Python + HTML.
                </p>
            </div>
        </section>
    )
