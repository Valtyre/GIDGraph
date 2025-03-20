'use client'
import Image from "next/image";
import {useState} from "react"
import TextBox from "./Elements/textBox";
import TopBar from "./Elements/TopBar";
import { getGeneInteractions } from "./api";


export default function Home() {
  const [message, setMessage] = useState("");


  
  
  return (
    <div>
      <TopBar></TopBar>
      <div className="flex flex-row">
        <TextBox header = "GID" fun = {getGeneInteractions}></TextBox>
        <TextBox header = "Semi-natural Language"></TextBox>
      </div>
    </div>
  )
}