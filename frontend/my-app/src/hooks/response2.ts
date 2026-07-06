{/* Generate a response received through continuous streaming (SSE) and emotion integration with emotion2vec */}
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useState } from 'react';

type responseProps = {
    messages : {role : string, content : string}[];
    interviewer : boolean;          // True : 1, False : 2
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
    displayTextGradual : Function;
    setMessages : (messages : (prev : any) => any[]) => void;
    emotion : string; 
}

const [blensdshapePath, setBlendshapePath] = useState<string | null>(null);

export async function getResponse({messages, interviewer, setMessagePopUp, setErrorPopUp, displayTextGradual, setMessages, emotion} : responseProps){
  const postProcessing = async (text : string) => {
    const response = await fetch("http://localhost/tts",{
      method : "POST",
      headers : {
        "Content-Type" : "application/json"
      },
      body : JSON.stringify({text : text, path : blensdshapePath})
    })

    const data = await response.json();
    setBlendshapePath(data.path);
    const audio = new Audio(data.audio);
    audio.play();
  };

  
  try{
      const interview_type = interviewer ? 1 : 2;  
      var count = 0;          // Count the number of chunks
      var partial_text = "";  // Text of 10 chunks to perform post-processing

      // Fetch a response from OpenAI
      await fetchEventSource("http://localhost:8000/response/stream", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept' : "text/event-stream",
        },
        body: JSON.stringify({input : messages, interview_type : interview_type, emotion : emotion}),

        onopen : async (res : Response) => {
          if (res.ok && res.status === 200) {
            console.log("Connection made ", res);
          } else if (
            res.status >= 400 &&
            res.status < 500 &&
            res.status !== 429
          ) {
            console.log("Client side error ", res);
          }
        },

        onmessage(event) {      // Data received from NLP
          const parsedData = JSON.parse(event.data);
          displayTextGradual({text : parsedData, setMessages});

          // Conditionally perform post-processing
          count += 1;
          partial_text += parsedData;
          if(count >= 10 && parsedData.trim() in ["!", ".", ";", ":", "?"]){  // Context retention
            console.log(partial_text);    
            postProcessing(partial_text);
            count = 0;
            partial_text = "";
          }
        },

        onclose() {
          console.log("Connection closed by the server");
        },

        onerror(err) {
          console.log("There was an error from server", err);
        },
      },)
    } catch (error){
      console.log(error);
    }
};  


