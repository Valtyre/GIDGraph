export default function TopBar() {
  return (
    <header 
      className="w-full bg-second flex items-center justify-between px-6 py-4 shadow-md border-b border-third/20"
      role="banner"
    >
      {/* App branding */}
      <div className="flex items-center gap-3">
        <h1 className="text-third text-3xl md:text-4xl font-bold tracking-tight">
          GIDGraph
        </h1>
        <span className="hidden sm:inline-block text-sm text-third/70 font-medium border-l border-third/30 pl-3">
          Gene Interaction Visualizer
        </span>
      </div>
    </header>
  );
}
