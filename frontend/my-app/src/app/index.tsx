import {useEffect, useRef, useState} from 'react';
import '../../global.css';

// Site used for audio recording: https://www.cybrosys.com/blog/how-to-implement-audio-recording-in-a-react-application
// Connection to web sockets : https://websocket.org/guides/frameworks/react/
// Web sockets: https://medium.com/@suganthi2496/fastapi-websockets-react-real-time-features-for-your-modern-apps-b8042a10fd90

export default function Index() {
  // Web Socket connections
  const ws = useRef<WebSocket | null>(null);  
  const wsResponse = useRef<WebSocket | null>(null);
  const wsAvatar = useRef<WebSocket | null>(null);
  const open = useRef<boolean>(false);     // Dealing with web sockets open and closing mutliple times
  
  const mediaStream = useRef<MediaStream | null>(null);        
  const mediaRecorder = useRef<MediaRecorder | null>(null);                         // Stream of media content (several tracks)
  const chunks = useRef<Blob[]>([]);                                                // Recorded audio
  const [recordedUrl, setRecordedUrl] = useState<string | undefined>(undefined);

  const [recordedText, setRecordedText] = useState('');
  const [messages, setMessages] = useState<{sender : string, message : string}[]>([]);

  useEffect(() => {
    if(open.current){
      return;
    }
    open.current = true;
    
    // Use secure WebSocket in production
    const wsUrl = "ws://127.0.0.1:8000/asr";
    const wsResponseUrl = "ws://127.0.0.1:8000/response";
    const wsAvatarUrl= "ws://127.0.0.1:8000/avatar"

    // ASR WebSocket
    ws.current = new WebSocket(wsUrl);

    // Handle the event the web socket connection opens
    ws.current.onopen = () => {console.log("WS open");};

    // Handle the event a message is sent
    ws.current.onmessage = (event) => {
      if(event.data == "Received input audio, processing ..."){
        displayTextGradual(event.data, "Attention : ");
      } else {
        displayTextGradual(event.data, "You : ");
      }

    };

    // Handle the event the connection closes
    ws.current.onclose = () => {console.log("WS closed");};

    // Response webSocket
    wsResponse.current = new WebSocket(wsResponseUrl);
    wsResponse.current.onopen = () => {console.log("WS response open");};
    wsResponse.current.onmessage = (event) => {
      displayTextGradual(event.data, "Bot : ");
    };
    wsResponse.current.onclose = () => {console.log("WS response closed");};

    // Avatar webSocket
    wsAvatar.current = new WebSocket(wsAvatarUrl);
    wsAvatar.current.onopen = () => {console.log("WS avatar open");};
    wsAvatar.current.onmessage = (event) => {};
    wsAvatar.current.onclose = () => {console.log("WS avatar closed");};
  
    // Cleanup
    return () => {
      ws.current?.close(1000, "unmounted");
      wsAvatar.current?.close(1000, "unmounted");
      wsResponse.current?.close(1000, "unmounted");
    };
  }, []);

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
          chunks.current, {type : 'audio/webm'}
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

    // Send the user input to OpenAI to generate a response
    if (wsResponse.current?.readyState === WebSocket.OPEN){
      wsResponse.current.send(recordedText);
    }

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
    <div className = "flex flex-col place-content-end items-start gap-4 p-6 h-full w-80 shadow-md shadow-gray-200 m-4">
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
        <div className = "flex flex-row gap-4 py-2">
          <input value = {recordedText} id = "textInput" onChange = {handleText} type = "text" className = "grow focus:border-blue-300 border-gray-300 bg-gray-50 text-gray-500 text-sm p-2 border-2 rounded-lg outline-none"/>
          <button className = "flex-none bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {sendText}> OK </button>
        </div>
        <audio className = "w-full" controls src = {recordedUrl}/>
        <div className = "flex flex-row items-center py-2 gap-4">
          <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {startRecording}> Start Recording </button>
          <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick= {stopRecording}> Stop recording </button>
        </div>
      </div>
    </div>
  );
}

