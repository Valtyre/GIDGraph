'use client'
import TopBar from "./Elements/TopBar";
import { SNLBox } from "./Elements/SNL/snlBox";
import NatrualLanguageBox from "./Elements/natrualLanguageBox";
import { useEffect } from "react";
import GeneNetworkGraph from "./graph";


function getSNL(str: string){
  fetch("http://localhost:8000/api/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: `"${str}"` }),
  })
    .then(response => response.json())
    .then(data => {
      console.log("Response from server:", data);
      // data.snl => your SNL output
      // data.graph => your graph nodes/edges
    });
}

export default function Home() {
  
  return (
    <div>
      <TopBar></TopBar>
      <div className="flex flex-row bg-blue-950 p-5 h-[400px]">
        <NatrualLanguageBox header = "GID" fun={getSNL}></NatrualLanguageBox>
        <SNLBox></SNLBox>
      </div>
        <GeneNetworkGraph fileName={""}/>
    </div>
  )
}