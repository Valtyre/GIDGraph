'use client'
import Image from "next/image";
import {useState} from "react"
import TextBox from "./Elements/textBox";
import TopBar from "./Elements/TopBar";
import { getGeneInteractions } from "./api";
import GeneInteractionBubble from "./Elements/geneInteractionBubble"
import { SNLBox } from "./snlBox";


export default function Home() {
  const [message, setMessage] = useState("");


  
  
  return (
    <div>
      <TopBar></TopBar>
      <div className="flex flex-row bg-blue-950 p-5 h-[400px]">
        <TextBox header = "GID" fun = {getGeneInteractions}></TextBox>
        <SNLBox></SNLBox>
      </div>
    </div>
  )
}