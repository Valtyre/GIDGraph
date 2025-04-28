

export function Infobox({ text }: { text: string }) {
    return (
      <div className="relative group inline-block">
        {/* Info icon */}
        <span className="cursor-pointer">&#9432;</span>
  
        {/* Tooltip popup */}
        <aside className="absolute z-10 hidden group-hover:block bg-third text-white text-sm rounded px-3 py-2 w-max max-w-[250px] top-full left-1/2 transform -translate-x-1/2 mt-2 shadow-lg">
          <p>{text}</p>
        </aside>
      </div>
    );
  }
  