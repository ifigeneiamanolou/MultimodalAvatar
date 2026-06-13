import { View, StyleSheet } from "react-native";
import { useRef, useState } from 'react';
import '../../global.css';

// Site used for audio recording: https://www.cybrosys.com/blog/how-to-implement-audio-recording-in-a-react-application

export default function Index() {
  const mediaStream = useRef(new MediaStream());        
  const mediaRecorder = useRef(new MediaRecorder(new MediaStream()));           // Stream of media content (several tracks)
  const chunks = useRef([new Blob()]);                                          // Recorded audio
  const [recordedUrl, setRecordedUrl] = useState('');

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
       mediaRecorder.current.onstop = (e) => {
          const recordedBlob = new Blob(
            chunks.current, {type : 'audio/webm'}
          )
          const url = URL.createObjectURL(recordedBlob);
          setRecordedUrl(url);
          chunks.current = [new Blob()];
       };

       // Begins recording data into audio blobs
       mediaRecorder.current.start();
    } catch (error){
       console.log(error);
    }
  };

  const stopRecording = () => {
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

