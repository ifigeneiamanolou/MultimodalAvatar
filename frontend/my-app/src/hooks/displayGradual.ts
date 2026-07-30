

type displayProps = {
    text : string | null;
    messageID : string;
    setMessages : (messages : (prev : any) => any[]) => void;
}

type Message = {content : string, running : boolean};
const queue = new Map<string, Message>();

const runReveal = (messageID : string, setMessages : displayProps['setMessages']) => {
  const state = queue.get(messageID);
  if(!state || state?.running){
    return;
  }

  // Change the state of the current message
  state.running = true;

  // Display the message gradually
  const display = setInterval(() => {
    const s = queue.get(messageID);
    // Check if the queue is empty
    if(!s || s.content.length === 0){
      if(s) s.running = false;
      clearInterval(display);
      return;
    }

    // Drop emotional tags
    const emotions = ["<laugh>", "<chuckle>", "<sigh>", "<cough>", "<sniffle>", "<groan>", "<yawn>", "<gasp>"];
    for(let i = 0; i < emotions.length; i ++){
      s.content = s.content.replace(emotions[i], "");
    }


    // Display the next character
    const nextChar = s.content[0];
    s.content = s.content.slice(1);
    setMessages(prev => 
      prev.map((m : {id : string, content : string, role : string}) =>
         (m.id === messageID ? {...m, content : m.content + nextChar} : m)
      )
    );
  
    if(s.content.length === 0){
      clearInterval(display);
      s.running = false;
      queue.delete(messageID);
    }
  
  }, 40);

};

export default function displayTextGradual({text, messageID, setMessages} : displayProps){
    if(!text){
      return;
    } 
    
    // Extract the element from the queue with the matching id
    const message = queue.get(messageID) ?? {content : "", running : false};

    // Modify the text
    message.content += text;

    // Modify the queue element
    queue.set(messageID, message);

    // Reveal the message with the current id
    runReveal(messageID, setMessages);
};