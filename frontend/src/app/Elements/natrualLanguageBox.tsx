import { useState } from "react";

export default function NatrualLanguageBox({ fun }: { fun?: (arg0: string) => void }) {
  const [text, setText] = useState("");

  return (
    <>
      <div className="flex flex-col mx-auto w-full p-5"> 
        <h1 className=" font-bold text-3xl text-second">
          Gene Interaction Discriptions
        </h1>
        <textarea
          className="bg-off border-third border-2 rounded-sm w-full p-3 h-full resize-none"
          value={text} 
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text here"
        />
        <button 
          onClick={() => {
            fun?.(text); 
            console.log("click")
          }} 
          className="bg-third font-bold rounded-sm mt-4 p-2 w-fit text-main hover:bg-second">
          Convert to Semi-Natural Language
        </button>
      </div>
    </>
  );
}
