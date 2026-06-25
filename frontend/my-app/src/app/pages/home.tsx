import React, {useEffect, useRef, useState} from 'react';
import Alert from '../components/AlertMessage';
import Success from '../components/SuccessMessage';

// Site used for audio recording: https://www.cybrosys.com/blog/how-to-implement-audio-recording-in-a-react-application
// Connection to web sockets : https://websocket.org/guides/frameworks/react/
// Web sockets: https://medium.com/@suganthi2496/fastapi-websockets-react-real-time-features-for-your-modern-apps-b8042a10fd90

export default function Home() {
  // Web Socket connection
  const ws = useRef<WebSocket | null>(null);  

  // Microphone recording
  const mediaStream = useRef<MediaStream | null>(null);        
  const mediaRecorder = useRef<MediaRecorder | null>(null);                         // Stream of media content (several tracks)
  const chunks = useRef<Blob[]>([]);                                                // Recorded audio
  const [recordedUrl, setRecordedUrl] = useState<string | undefined>(undefined);

  // Displayed chat
  const [recordedText, setRecordedText] = useState('');
  const [messages, setMessages] = useState<{sender : string, message : string}[]>([]);

  // Popups
  const [successPopUp, setSuccessPopUp] = useState(false);
  const [errorPopUp, setErrorPopUp] = useState(false);
  const [messagePopUp, setMessagePopUp] = useState('');

  // Toggle
  const [interviewer, setInterviewer] = useState(true);

  // Reset button
  const [waiting, setWaiting] = useState(false);

  // Feedback
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    // Use secure WebSocket in production
    const wsUrl = "ws://127.0.0.1:8000/asr";

    const socket = new WebSocket(wsUrl);
    ws.current = socket;
    ws.current.onopen = () => {console.log("WS open");};
    ws.current.onmessage = (event) => {
      console.log(event.data);
      // Display the transcripted audio input
      displayTextGradual(event.data, "You : ");

      // Generate a response and its coefficients and play the audio
      getResponse(event.data);
    };
    ws.current.onclose = () => {console.log("WS closed");};
  
    // Cleanup
    return () => {
      socket.close(1000, "unmounted");
    };
  }, []);

  const getResponse = async (text : string, feedback : boolean = false) => {
    try{
      // Fetch a response from OpenAI
      const interview_type = interviewer ? 1 : 2;
      setWaiting(true);           // Waiting for response from OpenAI

      const res = await fetch("http://localhost:8000/response", {
        method : "POST",
        body : JSON.stringify({input : text, session_id : "default", interview_type : interview_type}),
        headers: {"Content-Type": "application/json"}
      });
      setWaiting(false);

      const response = await res.json();
      displayTextGradual(response.data, "Bot : ");

      //Convert to speech and generate blendshape coefficients
      const responseTTS = await fetch("http://localhost:8000/tts", {
        method : "POST",
        body : JSON.stringify({input : response.data, session_id : "default"}),
        headers: {"Content-Type": "application/json"}
      });

      // Play the audio
      const result = await responseTTS.json();
      const base64string = result.data.audio;
      var audio = new Audio("data:audio/wav;base64," + base64string);       // use of data URL prefix
      try{
        audio.play();
      } catch (e) {
        console.log(e);
      }
    } catch (error){
      console.log(error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio : true});      // Prompt the user for permission
      mediaStream.current = stream;                                                  // Interface to easily record media (ie audio)
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/ogg;codecs=opus';
      mediaRecorder.current = new MediaRecorder(stream, {mimeType : mimeType});  
       
      // Input audio from the user
      mediaRecorder.current.ondataavailable = (e) => {
        if(e.data.size > 0){
          chunks.current.push(e.data);
        }
      };

      // Handle the ending of audio input
      mediaRecorder.current.onstop = async (e) => {
        const recordedBlob = new Blob(
          chunks.current, {type : mimeType}
        )
        const data = await recordedBlob.bytes()

        if (ws.current?.readyState === WebSocket.CLOSED){
          setMessagePopUp("No web socket connection found");
          setErrorPopUp(true);
        } else {
          ws.current?.send(data);
          setMessagePopUp("Audio sent");
          setSuccessPopUp(true);
        }

        // Render the audio element in the frontend
        const url = URL.createObjectURL(recordedBlob);
        setRecordedUrl(url);
        chunks.current = [];
      };

      // Begins recording data into audio blobs
      mediaRecorder.current.start();
    } catch (error){
      console.log('Error accessing the microphone', error);
    }
  };

  const stopRecording = async () => {
    if(mediaRecorder.current && mediaRecorder.current.state == 'recording'){
      mediaRecorder.current.stop();   // Stop media capture
    }
    if(mediaStream.current){
      mediaStream.current.getTracks().forEach((track) =>{
        track.stop();                 // Stop the track
      });
    }
  };

  const sendText = () => {
    // Show the user input
    displayTextGradual(recordedText, "You : ");

    // Send the query to openai and display the answer
    getResponse(recordedText);

    // Clear the input field
    setRecordedText('');
  };

  const displayTextGradual = (text : string = "", sender : string = "") => {
    setMessages(prev => [...prev, {sender : sender, message : ''}])
    var index = 0;
    const displayText = setInterval(() => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            sender,
            message : text.slice(0, index + 1)
          };
          return updated;
        });
        index = index + 1;
        if (index >= text.length - 1){
          clearInterval(displayText);
        }
    }, 120);
  };

  const newConversation = async () => {
    // Ensure bot response has been received
    if(waiting){
      setErrorPopUp(true);
      setMessagePopUp("Waiting for model response. Try again.");
      return;
    }

    // Save messages as a JSON object
    const type = interviewer ? "interviewer" : "interviewee";
    await fetch("http://localhost:8000/reset", {
        method : "POST",
        body : JSON.stringify({"interviewer" : type, "data" : messages}),
        headers: {"Content-Type": "application/json"}
    });

    // Empty the display
    setMessages([]);
  };

  const generateFeedback = async () => {
    // Ensure bot response has been received
    if(waiting){
      setErrorPopUp(true);
      setMessagePopUp("Waiting for model response. Try again.");
      return;
    }

    // Ensure the conversation has started

    // Generate feedback
    const type = interviewer ? "interviewer" : "interviewee";
    const res = await fetch("http://localhost:8000/feedback", {
        method : "POST",
        body : JSON.stringify({"interviewer" : type, "data" : messages}),
        headers: {"Content-Type": "application/json"}
    });
    
    // Display the feedback
    const response = await res.json();
    setFeedback(response.data);
  };

  const handleText = (e : React.ChangeEvent<HTMLInputElement>) => setRecordedText(e.target.value);

  return (
    <div>
      {/* Pop ups */}
      <div className = "fixed right-0 left-0 top-4 flex justify-center z-50">
        <Alert showPopup={errorPopUp} closePopup={()=>setErrorPopUp(false)} message = {messagePopUp}/>
        <Success showPopup={successPopUp} closePopup={()=>setSuccessPopUp(false)} message = {messagePopUp}/>
      </div>

      {/* Main page */}
      <div className = "flex flex-row h-screen pb-8 z-0">
        {/* Chat interaction */}
        <div className = "flex flex-col place-content-end items-start gap-4 p-6 h-full w-80 shadow-md shadow-gray-300 m-4 overflow-hidden">
          {/* Text conversation */}
          <div className = "flex-1 overflow-auto mb-4">
              {messages.length === 0 ? <p> Your conversation will appear here </p> : messages.map((msg, i) => (
                  <div className = "" key = {i}>
                    <span className = "">
                      <strong> {msg.sender} </strong> {msg.message}
                    </span>
                  </div>
                ))
              }
          </div>
            
            <div className = "flex flex-col flex-shrink-0">
              {/* Input through text */}
              <div className = "flex flex-row gap-4 py-4">
                <input value = {recordedText} placeholder= "Hello, let's start this interview" title = "User input" id = "textInput" onChange = {handleText} type = "text" className = "grow focus:border-blue-300 border-gray-300 bg-gray-50 text-gray-500 text-sm p-2 border-2 rounded-lg outline-none"/>
                <button className = "flex-none bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {sendText}> OK </button>
              </div>

              {/* Input through speech and ASR*/}
              <audio className = "w-full" controls src = {recordedUrl}/>
              <div className = "flex flex-row items-center py-4 gap-4">
                <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {startRecording}> Start Recording </button>
                <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick= {stopRecording}> Stop recording </button>
              </div>

              {/* Control buttons */}
              {/* Source: https://flowbite.com/docs/forms/toggle/ */}
              <div className = "flex flex-row justify-between">
                <label className="inline-flex items-center cursor-pointer">
                <input type="checkbox" value="" className="sr-only peer" onChange={() => {setInterviewer(!interviewer);}}/>
                <div className="relative w-9 h-5 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-buffer after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-black after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-200"></div>
                  <span className="select-none ms-3 text-sm font-medium text-heading">{interviewer ? "Interviewer (bot)" : "Interviewee (bot)"}</span>
                </label>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="size-6" onClick = {newConversation}>
                    <path d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" />
                </svg>
              </div>
          </div>
        </div>

        <div className = "flex flex-col flex-1 h-full">
          {/* Avatar */}
          <div className = "flex flex-1 basis-3/4">

          </div>

          {/* Feedback generation */}
          <div className = "flex flex-1 flex-row basis-1/4 shadow-md shadow-gray-300 mx-4 gap-4 p-4 ">
            {/* Feedback */}
            <div className = "flex grow bg-gray-50 border-gray-300 border-2 rounded-lg p-2">
               <p className = "text-gray-500 text-sm"> 
                {feedback === "" ? "Press feedback button ..." : feedback} 
               </p>
            </div>

            {/* Buttons to generate feedback */}
            <div className = "grid grid-rows-2 gap-4 place-items-center">
              <button className = "flex items-center bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
                <svg className = "fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z"/></svg>
                <span> Download</span>
              </button>
              <button onClick = {generateFeedback} className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
                <span> Feedback </span>
              </button> 
            </div>
         </div>
       </div> 
      </div>
    </div>
  );
}