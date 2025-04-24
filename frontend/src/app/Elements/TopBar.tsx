
export default function TopBar({
  onExport,
}: {
  onExport?: () => void;
}) {
  return (
    <header className="w-full bg-second flex items-center justify-between px-6 py-4">
      {/* app title */}
      <h1 className="text-main text-4xl font-bold">GIDGraph</h1>

      {/* export button – shown only when callback is provided */}
      {onExport && (
        <button
          onClick={onExport}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-4 py-2 rounded shadow"
        >
          Export GINML
        </button>
      )}
    </header>
  );
}
