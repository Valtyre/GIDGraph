export function AddButton({ add }: { add: () => void }) {
  return (
    <button
      className="btn btn-secondary mt-1 w-full border-dashed py-3 text-[color:var(--color-accent-strong)]"
      onClick={add}
      aria-label="Add new gene interaction"
    >
      <svg
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
      Add interaction row
    </button>
  );
}
