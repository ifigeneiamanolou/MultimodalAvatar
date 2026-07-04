{/* Generate a response received through continuous streaming (SSE) */}

type responseProps = {
    messages : {role : string, content : string}[];
    interviewer : boolean;          // True : 1, False : 2
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
    displayTextGradual : Function;
    setMessages : (messages : (prev : any) => any[]) => void;
}

import { fetchEventSource } from '@microsoft/fetch-event-source';

export async function getResponse({messages, interviewer, setMessagePopUp, setErrorPopUp, displayTextGradual, setMessages} : responseProps){
  try{
      // Fetch a response from OpenAI
      const interview_type = interviewer ? 1 : 2;   
      await fetchEventSource("http://localhost/response/stream", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept' : "text/event-stream",
        },
        body: JSON.stringify({input : messages, interview_type : interview_type}),
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


