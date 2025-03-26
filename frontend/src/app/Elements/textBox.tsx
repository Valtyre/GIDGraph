import { useState } from "react";

export default function TextBox({ header, fun }: { header: string; fun?: (arg0: string) => void }) {
  const [text, setText] = useState("");

  return (
    <>
      <div className="flex flex-col mx-auto w-full p-5 gap-1"> 
        <h1 className=" font-bold text-3xl text-white">
          {header}
        </h1>
        <textarea
          className="bg-white border-black border-2 rounded-sm w-full p-3 h-40 resize-none"
          value={text} 
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text here"
        />
        <button 
          onClick={() => fun?.(text)} 
          className="bg-white border-black border-2 rounded-sm mt-4 p-2 w-fit">
          Submit
        </button>
      </div>
    </>
  );
}
