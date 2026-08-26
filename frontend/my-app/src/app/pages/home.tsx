import React, {useEffect, useRef, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import Alert from '../components/AlertMessage';
import Success from '../components/SuccessMessage';
import useRecorder from '../../hooks/record';
import displayTextGradual from '../../hooks/displayGradual';
import MarkDown from 'react-markdown';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { PixelStreamingWrapper } from '../components/PixelStreamingWrapper';
import constants from '@/constants/app';

export default function Home() {
  // ====================== Constants ========================
  // Web sockets
  const ws = useRef<WebSocket | null>(null);

  // Displayed chat
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<{id : string, role : string, content : string}[]>([]);
  const nlpRunning = useRef(false);

  // Popups
  const [successPopUp, setSuccessPopUp] = useState(false);
  const [errorPopUp, setErrorPopUp] = useState(false);
  const [messagePopUp, setMessagePopUp] = useState('');

  // Toggle
  const [interviewer, setInterviewer] = useState(true);

  // Text displayed in the feedback box
  const [feedback, setFeedback] = useState('');

  // Navigation
  const navigate = useNavigate();

  // ======================= Hooks =========================
  const [audio, setAudio] = useState();
  const emotion = useRef('');
  const {
    stopRecording,
    record,
    recorderState,
  } = useRecorder({ setAudio });

  // ======================= Web Socket ======================
  useEffect(() => {
    reset();
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let keepAliveInterval: ReturnType<typeof setInterval>;

    const connectASR = async () => {
      const socket = new WebSocket(`${constants.WHISPER_URL}`);          // Elastic IP address
      ws.current = socket;
      ws.current.onopen = () => {console.log("ASR socket open");}

      // Keep sending ping messages to prevent closure
      keepAliveInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
              ws.current?.send('keep-alive');
          }
      }, 30000);

      ws.current.onmessage = async (e) => {    // Results of ASR
        console.log("data from ASR socket: ", e.data);
        const response = e.data;

        // Check the status code of the response
        if (response.ok && response.status === 200) {
          console.log("Connection made ", response);
        } else if (
          response.status >= 400 &&
          response.status < 500 &&
          response.status !== 429
        ) {
          console.log("Server side error ", response);
          setErrorPopUp(true);
          setMessagePopUp("Server side error. Try again.");
          return;
        }

        // Flag the user if no audio is detected
        if(response === ""){
          setErrorPopUp(true);
          setMessagePopUp("No voice detected. Try again.");
          return;
        }
          
        setMessages(prev => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "user",
            content: response,
          },
        ]);
      }
      ws.current.onerror = (e) => {console.log("ASR socket error : ", e.target);}
      
      ws.current.onclose = () => {
        console.log("ASR socket closed");
        ws.current = null;
        reconnectTimer = setTimeout(connectASR, 1000);   // Open again the web socket after 1sec
      }
    };

    connectASR();

    return () => {    // Cleanup
      clearTimeout(reconnectTimer);  
      clearInterval(keepAliveInterval);
      ws.current?.close(1000, "unmounted");
    };
  }, []);

  // Restart the asyncio queue in the backend
  const reset = async () => {
      await fetch(`${constants.BACKEND_SERVER_URL}/reset/queue`, {method: 'POST'});
  };

  const fetchData = async (input : {role : string, content : string}[]) => {
    console.log("CALLING NLP", new Date(), input);
    const interview_type = interviewer ? 1 : 2; 
    const msgID = startBotMessage();
    const emotionState = emotion.current ? emotion.current : "neutral";

    if(nlpRunning.current) {
      setErrorPopUp(true);
      setMessagePopUp("NLP is already running. Please wait for the response.");
      return;
    }

    nlpRunning.current = true;

    try{
      await fetchEventSource(`${constants.BACKEND_SERVER_URL}/response/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': "text/event-stream",
        },
        body: JSON.stringify({input, interview_type : interview_type, emotion : emotionState}),
        onopen: async (res : Response) => {
          if (res.ok && res.status === 200) {
            console.log("Connection made ", res, " with code ", res.status);
          } else if (
            res.status >= 400 &&
            res.status < 500 &&
            res.status !== 429
          ) {
            console.log("Client side error ", res, "with code ", res.status);
          }
        },
        onmessage(event) {
          console.log("Data from NLP", event.data);
          displayTextGradual({text : event.data, messageID : msgID, setMessages});
        },
        onclose() {
          console.log("Connection closed by the server");
        },
        onerror(err) {
          console.log("There was an error from server", err);
        },
      },)
    } finally {
      nlpRunning.current = false;
    }
  };

  const sendText = async () => {
    // Check if the input text is empty
    if(inputText === ""){
      setErrorPopUp(true);
      setMessagePopUp("No input text. Type something.");
      return;
    }

    const updatedMessages = [
      ...messages,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: inputText
      }
    ];

    setMessages(updatedMessages);

    // Trigger a response
    fetchData(updatedMessages);

    // Clear the input field
    setInputText('');
  };


  const handleText = (e : React.ChangeEvent<HTMLInputElement>) => setInputText(e.target.value);

  const startBotMessage = () => {
    const newID = crypto.randomUUID();
    setMessages(prev => [...prev, {id : newID, role : "assistant", content : ""}]);
    return newID;
  }

  const handleFeedback = async () => {
    // Ensure the conversation has started
    if(messages.length < 2){
        setErrorPopUp(true);
        setMessagePopUp("Complete at least 2 rounds of the interview");
        return;
    }

    // Generate feedback
    const type = interviewer ? 1 : 2;
    const res = await fetch(`${constants.BACKEND_SERVER_URL}/feedback`, {
        method : "POST",
        body : JSON.stringify({input : messages, interview_type : type}),
        headers: {"Content-Type": "application/json"}
    });
    
    // Display the feedback
    const response = await res.json();
    setFeedback(response.data);
  }

  const handleNew = async () => {
    // Save messages as a JSON object
    const type = interviewer ? 1 : 2;
    await fetch(`${constants.BACKEND_SERVER_URL}/reset`, {
        method : "POST",
        body : JSON.stringify({interview_type : type, input : messages}),
        headers: {"Content-Type": "application/json"}
    });

    // Empty the display
    setMessages([]);
  }

  const navigateMenu = () => {navigate('/menu')};

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

  const handleStopRecording = async () => {
    const base64string = await stopRecording();

    // Check the string is valid
    if (!base64string) {
      setErrorPopUp(true);
      setMessagePopUp("Could not get audio.");
      return;
    }

    // Check the websocket is open
    if(ws.current?.readyState !== WebSocket.OPEN){
      setMessagePopUp('Web socket is closed');
      setErrorPopUp(true);
      return;
    }

    // Check that no other nlp response is running
    if(nlpRunning.current) {
      setErrorPopUp(true);
      setMessagePopUp("NLP is already running. Please wait for the response.");
      return;
    }

    nlpRunning.current = true;

    // Send to whisper
    ws.current.send(base64string);

    // Send to OpenAI
    const interview_type = interviewer ? 1 : 2; 
    const msgID = startBotMessage();
    const emotionState = emotion.current ? emotion.current : "neutral";

    try{
      await fetchEventSource(`${constants.BACKEND_SERVER_URL}/response/audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': "text/event-stream",
        },
        body: JSON.stringify({
          input : base64string, 
          interview_type : interview_type, 
          emotion : emotionState, 
          messages : messages
        }),
        onopen: async (res : Response) => {
          if (res.ok && res.status === 200) {
            console.log("Connection made ", res, " with code ", res.status);
          } else if (
            res.status >= 400 &&
            res.status < 500 &&
            res.status !== 429
          ) {
            console.log("Client side error ", res, "with code ", res.status);
          }
        },
        onmessage(event) {
          console.log("Data from NLP", event.data);
          displayTextGradual({text : event.data, messageID : msgID, setMessages});
        },
        onclose() {
          console.log("Connection closed by the server");
        },
        onerror(err) {
          console.log("There was an error from server", err);
        },
      },)
    } finally {
      nlpRunning.current = false;
    }
  };

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
        <div className = "flex flex-col place-content-end gap-4 p-6 h-full w-96 shadow-md shadow-gray-300 m-4 overflow-hidden">
          {/* Text conversation display */}
          <div className = "flex-1 overflow-auto mb-4 w-full overflow-x-hidden">
            {messages.length === 0 ? <p> Your conversation will appear here </p> : messages.map((msg) => (
              <div className = "w-full min-w-0 break-words" key = {msg.id}>
                <span className = "break-words whitespace-pre-wrap">
                  <strong> {msg.role} </strong> {msg.content}
                </span>
              </div>
            ))}
          </div>
            
          <div className = "flex flex-col gap-4">
            {/* Input through text */}
            <div className = "flex flex-row gap-4 py-4">
              <input value = {inputText} placeholder= "Hello, let's start this interview" title = "User input" id = "textInput" onChange = {handleText} type = "text" className = "grow focus:border-blue-300 border-gray-300 bg-gray-50 text-gray-500 text-sm p-2 border-2 rounded-lg outline-none"/>
              <button className = "flex-none bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {sendText}> OK </button>
            </div>

            {/* Input through speech and ASR*/}
            <audio controls src = {audio}></audio>
            <button onClick = {recorderState.isRecording ? handleStopRecording : record} className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
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
        <div className = "flex flex-col flex-1 h-full m-4 gap-8">
          {/* Avatar (pixel streaming)*/}
          <div className = "flex flex-1 basis-3/4">
              <PixelStreamingWrapper
                  initialSettings={{
                      AutoPlayVideo: true,
                      AutoConnect: true,
                      ss: constants.SIGNALING_SERVER,    
                      StartVideoMuted: true,
                      HoveringMouse: true,
                      WaitForStreamer: true,
                      HideUI : false,
                  }}
              />
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