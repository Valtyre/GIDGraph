export default function ExportButton({ onExport, isLoading = false }: { onExport: () => void; isLoading?: boolean }) {
  return (
    <div className="mt-4 text-center">
      <button
        onClick={onExport}
        disabled={isLoading}
        className="btn btn-export px-5 py-2.5 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Export logical formulas to GINML format"
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Exporting...
          </>
        ) : (
          <>
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
          </>
        )}
      </button>
    </div>
  );
}