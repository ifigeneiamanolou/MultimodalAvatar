type feedbackProps = {
    waiting : boolean;
    interviewer : boolean;
    messages : {sender : string, message : string}[];
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
};

export async function generateFeedback ({waiting, interviewer, messages, setMessagePopUp, setErrorPopUp} : feedbackProps) {
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
    return response.data;
};