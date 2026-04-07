export function Infobox({ text }: { text: string }) {
  return (
    <div className="relative group inline-flex items-center ml-2" tabIndex={0}>
      {/* Info icon - styled circle with "i" */}
      <span 
        className="
          inline-flex items-center justify-center
          w-5 h-5 rounded-full
          bg-third/20 text-third
          text-xs font-bold
          cursor-help
          transition-colors duration-150
          group-hover:bg-third group-hover:text-white
          group-focus:bg-third group-focus:text-white
        "
        aria-label="More information"
      >
        i
      </span>

      {/* Tooltip popup */}
      <aside
        role="tooltip"
        className="
          absolute z-20 
          invisible opacity-0
          group-hover:visible group-hover:opacity-100
          group-focus-within:visible group-focus-within:opacity-100
          transition-all duration-200
          bg-third text-white text-sm leading-relaxed
          rounded-lg
          px-4 py-3 
          w-max max-w-[280px]
          top-full left-1/2 -translate-x-1/2 mt-2
          shadow-lg
          before:content-[''] before:absolute before:bottom-full before:left-1/2 before:-translate-x-1/2
          before:border-8 before:border-transparent before:border-b-third
        "
      >
        <p className="m-0">{text}</p>
      </aside>
    </div>
  );
}