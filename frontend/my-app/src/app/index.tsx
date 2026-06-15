import {useEffect, useRef, useState, useCallback} from 'react';
import '../../global.css';

// Site used for audio recording: https://www.cybrosys.com/blog/how-to-implement-audio-recording-in-a-react-application
// Connection to web sockets : https://websocket.org/guides/frameworks/react/
// Web sockets: https://medium.com/@suganthi2496/fastapi-websockets-react-real-time-features-for-your-modern-apps-b8042a10fd90

export default function Index() {
  const ws = useRef<WebSocket | null>(null);                                        // Web Socket connection
  const mediaStream = useRef<MediaStream | null>(null);        
  const mediaRecorder = useRef<MediaRecorder | null>(null);                         // Stream of media content (several tracks)
  const chunks = useRef<Blob[]>([]);                                                // Recorded audio
  const [recordedUrl, setRecordedUrl] = useState<string | undefined>(undefined);
  const [recordedText, setRecordedText] = useState('Waiting for recording'); 

  useEffect(() => {
    // Use secure WebSocket in production
    const wsUrl = "ws://127.0.0.1:8000/asr";
    ws.current = new WebSocket(wsUrl);

    // Handle the event the web socket connection opens
    ws.current.onopen = () => {
      console.log("WS open");
    };

    // Handle the event a message is sent
    ws.current.onmessage = (event) => {
      setRecordedText(event.data);    // Record the data received
    };

    // Handle the event the connection closes
    ws.current.onclose = () => {
      console.log("WS closed");
    };

    ws.current.onerror = (error) => {
      console.log(error);
    }

    // Cleanup (no crash if null)
    return () => {ws.current?.close(1000, "unmounted");};
  }, []);

  const startRecording = async () => {
    setRecordedText('');
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

  return (
    <div className = "flex flex-col place-content-end items-start gap-4 p-6 h-full w-fit shadow-md shadow-gray-200 m-4">
      <div className = "flex flex-col gap-4">
        <p> {recordedText} </p>
        <input type = "text" className = "focus:border-blue-300 border-gray-300 bg-gray-50 text-gray-500 text-sm p-2 border-2 rounded-lg outline-none" defaultValue = "Enter a prompt for the bot "/>
        <audio className = "w-full" controls src = {recordedUrl}/>
        <div className = "flex flex-row items-center p-2 gap-4">
          <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick = {startRecording}> Start Recording </button>
          <button className = "bg-black text-white rounded-lg py-2 px-4 hover:shadow-white hover:bg-slate-700" onClick= {stopRecording}> Stop recording </button>
        </div>
      </div>
    </div>
  );
}

