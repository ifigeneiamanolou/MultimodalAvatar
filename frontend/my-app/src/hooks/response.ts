{/* Generate a response at once */}

type responseProps = {
    messages : {role : string, content : string}[];
    interviewer : boolean;          // True : 1, False : 2
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
    displayTextGradual : Function;
    setMessages : (messages : (prev : any) => any[]) => void;
}

export async function getResponse({messages, interviewer, setMessagePopUp, setErrorPopUp, displayTextGradual, setMessages} : responseProps){
    
  try{
      // Fetch a response from OpenAI
      const interview_type = interviewer ? 1 : 2;   
      const res = await fetch("http://localhost:8000/response", {
        method : "POST",
        body : JSON.stringify({input : messages, interview_type : interview_type}),
        headers: {"Content-Type": "application/json"}
      });

      // Display the bot response
      const body = await res.json()
      const data = body.data;
      displayTextGradual({text : data, sender : "assistant", setMessages})

      // Perform TTS 
      const resTTS = await fetch("http://localhost:8000/tts", {
        method : "POST",
        body : JSON.stringify({input : messages, interview_type : interview_type}),
        headers: {"Content-Type": "application/json"}
      });

      const bodyTTS = await resTTS.json()
      const audio = body.data.audio;

      // Perform emotion recognition

      // Generate artkit coefficients
    } catch (error){
      console.log(error);
    }

};  

