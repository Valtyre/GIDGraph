
export function AddButton({add} : {add: () => void}){
  return (
    <button 
      className="
        btn btn-primary
        w-full max-w-[300px] mx-auto
        py-2.5 mt-2
        text-sm font-semibold
      "
      onClick={add}
      aria-label="Add new gene interaction"
    >
      <svg 
        className="w-4 h-4" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
      Add Interaction
    </button>
  )
}