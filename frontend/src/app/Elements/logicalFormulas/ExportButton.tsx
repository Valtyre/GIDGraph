export default function ExportButton({ onExport }: { onExport: () => void }) {
  return (
    <div className="mt-4 text-center">
      <button
        onClick={onExport}
        className="btn btn-export px-5 py-2.5 shadow-sm"
        aria-label="Export logical formulas to GINML format"
      >
        <svg 
          className="w-4 h-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Export GINML
      </button>
    </div>
  );
}