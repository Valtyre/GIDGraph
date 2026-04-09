export default function TopBar() {
  return (
    <header
      className="relative z-20 mx-auto w-full max-w-[1600px] px-4 pt-4 sm:px-6 lg:px-10 lg:pt-6"
      role="banner"
    >
      <div className="glass-panel flex animate-enter items-center justify-between rounded-[1.75rem] border px-5 py-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-4">
          <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-[1.2rem] border border-[color:var(--color-line)] bg-white/60 shadow-[0_10px_30px_rgba(31,95,114,0.12)]">
            <span className="font-[family:var(--font-display)] text-3xl leading-none text-[color:var(--color-accent-strong)]">
              G
            </span>
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              <h2 className="font-[family:var(--font-display)] text-4xl leading-none tracking-[-0.04em] text-foreground">
                GIDGraph
              </h2>
            </div>
            <p className="mt-1 text-sm text-[color:var(--color-ink-soft)] sm:text-base">
              Gene interaction authoring and visualization.
            </p>
          </div>
        </div>

        <div className="hidden items-center gap-3 lg:flex">
          <div className="status-pill">
            <span className="status-dot" />
            Systems biology
          </div>
        </div>
      </div>
    </header>
  );
}
