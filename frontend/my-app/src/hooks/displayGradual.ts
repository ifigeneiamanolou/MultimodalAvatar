type displayProps = {
    text : string;
    sender : string;
    setMessages : (messages : (prev : any) => any[]) => void;
}

export default function displayTextGradual({text, sender, setMessages} : displayProps){
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