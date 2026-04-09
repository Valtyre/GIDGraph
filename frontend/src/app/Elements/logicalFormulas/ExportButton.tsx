export default function ExportButton({
  onExport,
  isLoading = false,
}: {
  onExport: () => void;
  isLoading?: boolean;
}) {
  return (
    <div className="mt-4 rounded-[1.4rem] border border-[color:rgba(195,155,93,0.28)] bg-[linear-gradient(135deg,rgba(195,155,93,0.16)_0%,rgba(255,255,255,0.9)_100%)] p-4">
      <button
        onClick={onExport}
        disabled={isLoading}
        className="btn btn-export w-full justify-center disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Export logical formulas to GINML format"
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Preparing export
          </>
        ) : (
          <>
            <svg
              className="h-4 w-4"
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
