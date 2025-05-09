export default function ExportButton({ onExport }: { onExport: () => void }) {
  return (
    <div className="mt-4 text-center">
      <button
        onClick={onExport}
        className="text-white font-semibold px-4 py-2 rounded shadow export-button bg-[#529CCB] hover:bg-[#468BB3]"
      >
        Export GINML
      </button>
    </div>
  );
}