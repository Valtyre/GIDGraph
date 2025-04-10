'use client'
import TopBar from "./Elements/TopBar";
import { SNLBox } from "./Elements/SNL/snlBox";
import NatrualLanguageBox from "./Elements/natrualLanguageBox";
import { useEffect } from "react";
import GeneNetworkGraph from "./graph";




export default function Home() {
  
  return (
    <div>
      <TopBar></TopBar>
      <div className="flex flex-row bg-blue-950 p-5 h-[400px]">
        <NatrualLanguageBox header = "GID"></NatrualLanguageBox>
        <SNLBox></SNLBox>
      </div>
        <GeneNetworkGraph fileName={""}/>
    </div>
  )
}