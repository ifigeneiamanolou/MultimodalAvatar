{/*
    Second version of the home page with continuous streaming of the LLM response which is displayed it using microsoft/fetch-event-
    source to handle the incoming SSE messages
    
*/}

import React, {useEffect, useRef, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import Alert from '../components/AlertMessage';
import Success from '../components/SuccessMessage';
import useRecorder from '../../hooks/record';
import displayTextGradual from '../../hooks/displayGradual';
import {generateFeedback} from '../../hooks/feedback';
import {newConversation} from '../../hooks/reset';
import {getResponse} from '../../hooks/response';
import MarkDown from 'react-markdown';
import '../../../global.css';
import fetchEventSource from '@microsoft/fetch-event-source';

export default function Home() {
  // ====================== Constants ========================
  // Web sockets
  const ws = useRef<WebSocket | null>(null);
  const wsTTS = useRef<WebSocket | null>(null);                                     // Allows continuous streaming

  // Displayed chat
  const [recordedText, setRecordedText] = useState('');
  const [messages, setMessages] = useState<{role : string, content : string}[]>([]);

  // Popups
  const [successPopUp, setSuccessPopUp] = useState(false);
  const [errorPopUp, setErrorPopUp] = useState(false);
  const [messagePopUp, setMessagePopUp] = useState('');

  // Toggle
  const [interviewer, setInterviewer] = useState(true);

  // Waiting for feedback
  const [waiting, setWaiting] = useState(false);

  // Text displayed in the feedback box
  const [feedback, setFeedback] = useState('');

  // Changing pages
  const navigate = useNavigate();

  // Loaders
  const [waitingNLP, setWaitingNLP] = useState(false);
  const [waitingASR, setWaitingASR] = useState(false);
  const [waitingFeedback, setWaitingFeedback] = useState(false);

  // ======================= Imports =========================
  // Microphone recording
  const {
    stopRecording,
    record,
    recorderState,
  } = useRecorder({setMessagePopUp, setErrorPopUp, setSuccessPopUp, ws});
  const [audio, setAudio] = useState();


  // ======================= Web Socket ======================
  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let reconnectTimerTTS: ReturnType<typeof setTimeout>;

    const connectASR = () => {
      const socket = new WebSocket("ws://127.0.0.1:8000/asr");
      ws.current = socket;
      ws.current.onopen = () => {console.log("ASR socket open");}
      ws.current.onmessage = async (e) => {    // Results of ASR
        console.log("data from ASR socket: ", e.data);
        const response = e.data;

        // Show the transcribed user input
        const userMessage =  {role : "user", content : response};
        displayTextGradual({text : response, sender : "user", setMessages});    
      }
      ws.current.onerror = (e) => {console.log("ASR socket error : ", e.target);}
      ws.current.onclose = () => {
        console.log("ASR socket closed");
        ws.current = null;
        reconnectTimer = setTimeout(connectASR, 1000);   // Open again the web socket after 1sec
      }
    };

    const connectTTS = () => {
      const socket = new WebSocket("ws://127.0.0.1:8000/tts/stream");
      wsTTS.current = socket;
      wsTTS.current.onopen = () => {console.log("TTS socket open");}
      wsTTS.current.onerror = (e) => {console.log("TTS socket error : ", e.target);}
      wsTTS.current.onmessage = (e) => {
        console.log("message from TTS socket : ", e);
        if(e.data instanceof Blob){
          const url = URL.createObjectURL(e.data);
          const audio = new Audio(url);
          audio.play();
        }
      }
      wsTTS.current.onclose = () => {
        console.log("TTS socket closed");
        wsTTS.current = null;
        reconnectTimerTTS = setTimeout(connectASR, 5000);   // Open again the web socket after 5sec
      }
    };

    connectASR();
    connectTTS();

    return () => {
      clearTimeout(reconnectTimer);  
      clearTimeout(reconnectTimerTTS);
      ws.current?.close(1000, "unmounted");
      wsTTS.current?.close(1000, "unmounted");
    };
  }, []);

  // Handling incoming text queries
  const sendText = async () => {
    // Show the user input
    const userMessage =  {role : "user", content : recordedText};
    displayTextGradual({text : recordedText, sender : "user", setMessages});

    // Send the query to openai and display the answer
    await getResponse({
      messages : [...messages, userMessage],
      interviewer,
      setMessagePopUp,
      setErrorPopUp,
      displayTextGradual,
      setMessages
    })

    // Clear the input field
    setRecordedText('');
  };

  const handleText = (e : React.ChangeEvent<HTMLInputElement>) => setRecordedText(e.target.value);

  const handleFeedback = async () => {
    setFeedback(
      await generateFeedback({waiting, interviewer, messages, setMessagePopUp, setErrorPopUp})
    );
  }

  const handleNew = async () => {
    newConversation({waiting, setMessagePopUp, setErrorPopUp, interviewer, messages, setMessages})
  }

  const downloadFeedback = () => {
    // Create a blob object of mime type text and attach to a temporary anchor element, triggered programmatically
    const element = document.createElement("a");
    const file = new Blob([feedback === "" ? "No feedback generated" : feedback], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = "myFeedback.txt";
    document.body.appendChild(element); // Required for this to work in FireFox

    // Ensure the conversation has started
    if(messages.length < 2){
        setErrorPopUp(true);
        setMessagePopUp("Complete at least 2 rounds of the interview");
        return;
    } else{
      element.click();
    }
  };

  const navigateMenu = () => { navigate('/menu'); };

  return (
    <>
      {/* Pop ups */}
      <div className = "fixed right-0 left-0 top-4 flex justify-center z-50">
        <Alert showPopup={errorPopUp} closePopup={()=>setErrorPopUp(false)} message = {messagePopUp}/>
        <Success showPopup={successPopUp} closePopup={()=>setSuccessPopUp(false)} message = {messagePopUp}/>
      </div>

      {/* Home button */}
      <div className = "fixed top-4 right-4 z-50">
        <svg xmlns="http://www.w3.org/2000/svg" onClick = {navigateMenu} viewBox="0 0 24 24" fill="currentColor" className="size-6 cursor-pointer">
          <path d="M11.47 3.841a.75.75 0 0 1 1.06 0l8.69 8.69a.75.75 0 1 0 1.06-1.061l-8.689-8.69a2.25 2.25 0 0 0-3.182 0l-8.69 8.69a.75.75 0 1 0 1.061 1.06l8.69-8.689Z" />
          <path d="m12 5.432 8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 0 1-.75-.75v-4.5a.75.75 0 0 0-.75-.75h-3a.75.75 0 0 0-.75.75V21a.75.75 0 0 1-.75.75H5.625a1.875 1.875 0 0 1-1.875-1.875v-6.198a2.29 2.29 0 0 0 .091-.086L12 5.432Z" />
        </svg>
      </div>

      {/* Main page */}
      <div className = "flex flex-row h-screen pb-8 z-0">
        {/* Chat interaction */}
        <div className = "flex flex-col place-content-end gap-4 p-6 h-full w-100 shadow-md shadow-gray-300 m-4 overflow-hidden">
          {/* Text conversation */}
          <div className = "flex-1 overflow-auto mb-4 w-full overflow-x-hidden">
            {messages.length === 0 ? <p> Your conversation will appear here </p> : messages.map((msg, i) => (
              <div className = "w-full min-w-0 break-words" key = {i}>
                <span className = "break-words whitespace-pre-wrap">
                  <strong> {msg.role} </strong> {msg.content}
                </span>
              </div>
            ))}
          </div>
            
          <div className = "flex flex-col gap-4">
            {/* Input through text */}
            <div className = "flex flex-row gap-4 py-4">
              <input value = {recordedText} placeholder= "Hello, let's start this interview" title = "User input" id = "textInput" onChange = {handleText} type = "text" className = "grow focus:border-blue-300 border-gray-300 bg-gray-50 text-gray-500 text-sm p-2 border-2 rounded-lg outline-none"/>
              <button className = "flex-none bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {sendText}> OK </button>
            </div>

            {/* Input through speech and ASR*/}
            <audio controls src = {audio}></audio>
            <button onClick = {recorderState.isRecording ? stopRecording : record} className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
              {recorderState.isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>

            {/* Control buttons */}
            {/* Source: https://flowbite.com/docs/forms/toggle/ */}
            <div className = "flex flex-row justify-between">
              <label className="inline-flex items-center cursor-pointer">
              <input type="checkbox" value="" className="sr-only peer" onChange={() => {setInterviewer(!interviewer);}}/>
              <div className="relative w-9 h-5 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-buffer after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-black after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-200"></div>
                <span className="select-none ms-3 text-sm font-medium text-heading">{interviewer ? "Interviewer (bot)" : "Interviewee (bot)"}</span>
              </label>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="size-6 cursor-pointer" onClick = {handleNew}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
            </div>
          </div>
        </div>

        {/* Right part of the main page */}
        <div className = "flex flex-col flex-1 h-full">
          {/* Avatar */}
          <div className = "flex flex-1 basis-3/4">

          </div>

          {/* Feedback generation */}
          <div className = "flex flex-1 flex-row basis-1/4 shadow-md shadow-gray-300 mx-4 gap-4 p-4 ">
            {/* Feedback */}
            <div className = "flex grow bg-gray-50 text-gray-500 test-sm border-gray-300 border-2 rounded-lg p-2 overflow-auto">
              {feedback ? <MarkDown children= {feedback} rehypePlugins = {[]} remarkPlugins = {[]}/> : <p> Feedback will appear here ... </p>}   
            </div>

            {/* Buttons to generate feedback */}
            <div className = "grid grid-rows-2 gap-4 place-items-center">
              <button className = "flex items-center bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {downloadFeedback}>
                <svg className = "fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z"/></svg>
                <span> Download</span>
              </button>
              <button onClick = {handleFeedback} className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
                <span> Feedback </span>
              </button> 
            </div>
          </div>
        </div> 
      </div>
    </>
  );
}