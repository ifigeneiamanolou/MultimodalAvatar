type displayProps = {
    text : string | null;
    sender : string | null;
    setMessages : (messages : (prev : any) => any[]) => void;
}

export default function displayTextGradual({text, sender, setMessages} : displayProps){
    if(sender){
      setMessages(prev => [...prev, {role : sender, content : ''}]);
    } else {
      sender = "assistant";
    }

    if(text){
      var index = 0;
      const displayText = setInterval(() => {
          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role : sender,
              content : text.slice(0, index + 1)
            };
            return updated;
          });
          index = index + 1;
          if (index >= text.length){
            clearInterval(displayText);
          }
      }, 80);
    } 
};