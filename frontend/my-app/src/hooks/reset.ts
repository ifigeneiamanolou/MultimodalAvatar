import { Dispatch, SetStateAction } from "react";

type resetProps = {
    waiting : boolean;
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
    interviewer : boolean;
    messages : {sender : string, message : string}[];
    setMessages : Dispatch<SetStateAction<{ sender: string; message: string; }[]>>;
}

export async function newConversation ({waiting, setMessagePopUp, setErrorPopUp, interviewer, messages, setMessages} : resetProps) {
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