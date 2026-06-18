import {useEffect, useRef, useState} from 'react';
import '../../global.css';
import AvatarComponent from './components/AvatarComponent'

// Site used for audio recording: https://www.cybrosys.com/blog/how-to-implement-audio-recording-in-a-react-application
// Connection to web sockets : https://websocket.org/guides/frameworks/react/
// Web sockets: https://medium.com/@suganthi2496/fastapi-websockets-react-real-time-features-for-your-modern-apps-b8042a10fd90
// UE5 integration : https://dev.to/imaijiro/how-to-implement-socket-communication-in-unreal-engine-and-nodejs-4m0j

export default function Index() {
  // Web Socket connection
  const ws = useRef<WebSocket | null>(null);  
  const open = useRef<boolean>(false);     // Dealing with web socket open and closing mutliple times

  // Microphone recording
  const mediaStream = useRef<MediaStream | null>(null);        
  const mediaRecorder = useRef<MediaRecorder | null>(null);                         // Stream of media content (several tracks)
  const chunks = useRef<Blob[]>([]);                                                // Recorded audio
  const [recordedUrl, setRecordedUrl] = useState<string | undefined>(undefined);

  // Displayed chat
  const [recordedText, setRecordedText] = useState('');
  const [messages, setMessages] = useState<{sender : string, message : string}[]>([]);

  // Avatar
  const modelSrc = 'https://readyplayerme.github.io/visage/male.glb';

  useEffect(() => {
    if(open.current){
      return;
    }
    open.current = true;
    
    // Use secure WebSocket in production
    const wsUrl = "ws://127.0.0.1:8000/asr";
    ws.current = new WebSocket(wsUrl);
    ws.current.onopen = () => {console.log("WS open");};
    ws.current.onmessage = (event) => {
      if(event.data == "Received input audio, processing ..."){
        displayTextGradual(event.data, "Attention : ");
      } else{
        displayTextGradual(event.data, "You : ");
      }

      getResponse(event.data);
    };
    ws.current.onclose = () => {console.log("WS closed");};
  
    // Cleanup
    return () => {
      ws.current?.close(1000, "unmounted");
    };
  }, []);

  const getResponse = async (text : string) => {
    try{
      // Fetch a response from OpenAI
      const res = await fetch("http://localhost:8000/response", {
        method : "POST",
        body : JSON.stringify({input : text, session_id : "default"}),
        headers: {"Content-Type": "application/json"}
      });

      // Display the response
      const data = await res.json();
      displayTextGradual(data["response"], "Bot : ");

      // Convert to speech and generate animations
      await fetch("http://localhost:8000/tts", {
        method : "POST",
        body : JSON.stringify({input : data["response"], session_id : "default"}),
        headers: {"Content-Type": "application/json"}
      });
    } catch (error){
      console.log(error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio : true});      // Prompt the user for permission
      mediaStream.current = stream;                                                  // Interface to easily record media (ie audio)
      mediaRecorder.current = new MediaRecorder(stream);
       
      // Input audio from the user
      mediaRecorder.current.ondataavailable = (e) => {
        if(e.data.size > 0){
          chunks.current.push(e.data);
        }
      };

      // Handle the ending of audio input
      mediaRecorder.current.onstop = async (e) => {
        const recordedBlob = new Blob(
          chunks.current, {type : 'audio/mp3'}
        )

        const data = await recordedBlob.arrayBuffer();

        if (ws.current?.readyState === WebSocket.OPEN){
          ws.current.send(data);
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

  const displayTextGradual = (text : string, sender : string = "") => {
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

  const handleText = (e : React.ChangeEvent<HTMLInputElement>) => setRecordedText(e.target.value);

  return (
    <div className = "flex flex-row h-screen py-6">
      {/* Chat interaction */}
      <div className = "flex flex-col place-content-end items-start gap-4 p-6 h-full w-80 shadow-md shadow-gray-300 m-4">
        {/* Text conversation */}
        <div className = "flex flex-col gap-4">
          <div className = "scroll-smooth">
            {messages.length === 0 ? <p> Your conversation will appear here </p> : messages.map((msg, i) => (
                <div className = "" key = {i}>
                  <span className = "">
                    <strong> {msg.sender} </strong> {msg.message}
                  </span>
                </div>
              ))
            }
          </div>

          {/* Input through text */}
          <div className = "flex flex-row gap-4 py-2">
            <input value = {recordedText} placeholder= "Hello, let's start this interview" title = "User input" id = "textInput" onChange = {handleText} type = "text" className = "grow focus:border-blue-300 border-gray-300 bg-gray-50 text-gray-500 text-sm p-2 border-2 rounded-lg outline-none"/>
            <button className = "flex-none bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {sendText}> OK </button>
          </div>

          {/* Input through speech and ASR*/}
          <audio className = "w-full" controls src = {recordedUrl}/>
          <div className = "flex flex-row items-center py-2 gap-4">
            <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {startRecording}> Start Recording </button>
            <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick= {stopRecording}> Stop recording </button>
          </div>
        </div>
      </div>

      <div className = "flex flex-col flex-1 h-full">
        {/* Avatar */}
        <div className = "flex flex-1 basis-3/4">
            <AvatarComponent modelSrc = {modelSrc}>

            </AvatarComponent>
        </div>

        {/* Feedback generation */}
        <div className = "flex flex-1 flex-row basis-1/4 gap-4 shadow-md shadow-gray-300 m-4 p-4">
          {/* Feedback */}
          <div className = "flex grow bg-gray-50 border-gray-300 border-2 rounded-lg"> </div>

          {/* Buttons to generate feedback */}
          <div className = "grid grid-rows-2 gap-4 place-items-center">
            <button className = "flex items-center bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
              <svg className = "fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z"/></svg>
              <span> Download</span>
            </button>
            <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700">
              <span> Feedback </span>
            </button> 
          </div>

        </div>
      </div>
      
    </div>
  );
}

