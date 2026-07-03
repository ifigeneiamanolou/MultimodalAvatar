type feedbackProps = {
    waiting : boolean;
    interviewer : boolean;
    messages : {role : string, content : string}[];
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
    if(messages.length < 2){
        setErrorPopUp(true);
        setMessagePopUp("Complete at least 2 rounds of the interview");
        return;
    }

    // Generate feedback
    const type = interviewer ? 1 : 2;
    const res = await fetch("http://localhost:8000/feedback", {
        method : "POST",
        body : JSON.stringify({input : messages, interview_type : type}),
        headers: {"Content-Type": "application/json"}
    });
    
    // Display the feedback
    const response = await res.json();
    return response.data;
};