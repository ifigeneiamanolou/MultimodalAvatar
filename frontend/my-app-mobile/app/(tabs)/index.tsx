import { View, TouchableOpacity, TextInput, Alert, } from 'react-native'; 
import '../../global.css';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { useRef, useState, useEffect, } from 'react';
import Icon from 'react-native-vector-icons/FontAwesome';
import useRecorder from '@/hooks/record';
import uuid from 'react-native-uuid';
import WebView from 'react-native-webview';

const showAlert = (title : string, message : string) => {
    Alert.alert(
      title,
      message,
      [
        { text: "OK", onPress: () => console.log("OK Pressed") }
      ]
    );
};

export default function Index(){
    // Placeholder for input text
    const [text, onChangeText] = useState('');
    const [messages, setMessages] = useState<Map<string, {role : string, content : string}>>(new Map());
    const nlpRunning = useRef(false);

    // Web socket connection with whisper
    const ws = useRef<WebSocket | null>(null);

    // Resulting emotion label from emotion2vec
    const emotion = useRef('');

    // Connection to the web socket
    useEffect(() => {
        let reconnectTimer: ReturnType<typeof setTimeout>;
        let keepAliveInterval: ReturnType<typeof setInterval>;
    
        const connectASR = async () => {
          const socket = new WebSocket("ws://3.129.236.140:8000/asr");          // Elastic IP address
          ws.current = socket;
          ws.current.onopen = () => {console.log("ASR socket open");}
    
          // Keep sending ping messages to prevent closure
          keepAliveInterval = setInterval(() => {
              if (ws.current?.readyState === WebSocket.OPEN) {
                  ws.current?.send('keep-alive');
              }
          }, 30000);
    
          ws.current.onmessage = async (e) => {    // Results of ASR
            console.log("data from ASR socket: ", e.data);
            const response = e.data;
    
            // Check the status code of the response
            if (response.ok && response.status === 200) {
              console.log("Connection made ", response);
            } else if (
              response.status >= 400 &&
              response.status < 500 &&
              response.status !== 429
            ) {
              showAlert('Error', 'Error when using Whisper');
              return;
            }
    
            // Flag the user if no audio is detected
            if(response === ""){
              showAlert('Error', 'No voice detected. Try again.');
            } else {
              const id = uuid.v4();
              setMessages(messages.set(id, {role : 'user', content : response}));
              fetchData();
            }
          }
          ws.current.onerror = (e) => {console.log("ASR socket error : ", e.target);}
          
          ws.current.onclose = () => {
            console.log("ASR socket closed");
            ws.current = null;
            reconnectTimer = setTimeout(connectASR, 1000);   // Open again the web socket after 1sec
          }
        };
    
        connectASR();
    
        return () => {    // Cleanup
          clearTimeout(reconnectTimer);  
          clearInterval(keepAliveInterval);
          ws.current?.close(1000, "unmounted");
        };
    }, []);

    // Handle user input text
    const sendText = async () => {
        // Check if the input text is empty
        if(text === ""){
            showAlert('Error', 'Type something first!');
            return;
        }

        // Update the map of sentences
        const id = uuid.v4();
        setMessages(messages.set(id, {role : 'user', content : text}));

        // Fetch a response from OpenAI 
        fetchData();

        // Clear the input field
        onChangeText('');
    };

    // Fetch an NLP response
    const fetchData = async () => {
        const emotionState = emotion.current ? emotion.current : "neutral";
        const input = Array.from(messages.values());

        if(nlpRunning.current) {
            showAlert('Error', 'Waiting for the bot to respond first!')
        }

        nlpRunning.current = true;

        var id = ""
        try{
            const res = await fetch("http:/192.168.1.188:8000/response/stream/mobile", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({emotion : emotionState, input : input, interview_type : 1})
            });

            // Handle the response from emotion recognition endpoint
            if(res.ok && res.status == 200){
                const nlpResponse  = await res.json();
                console.log("Connection made ", res, " with code ", res.status);

                // Create a new entry in the array messages
                id = uuid.v4()
                setMessages(messages.set(id, {role : 'user', content : nlpResponse}));
            } else{
                console.log('Error during nlp response generation with status ', res.status);
                showAlert('Error', 'Error during nlp response');
            }
        } catch (e){
            console.log('Error connecting to the local backend server ', e);
            showAlert('Error', 'Server connection issue');
        } finally {
            nlpRunning.current = false;
        }
    }; 

    const handleFeedback = async () => {
        // Ensure the conversation has started
        if(messages){
            if(messages.entries.length < 2){
                showAlert('Error', 'Complete at least 2 interview rounds!');
                return;
            }
        }

        const type = 1;
        var response = "";
        const input = Array.from(messages.values());
        try{
            const res = await fetch("http:/192.168.1.188:8000/feedback", {
                method : "POST",
                body : JSON.stringify({input : input, interview_type : type}),
                headers: {"Content-Type": "application/json"}
            });

            response = await res.json();
        } catch (err){
            console.log("fetchData error:", err);
            showAlert('Error', 'Could not reach the server');
            return;
        }  
    };

    const handleNew = async () => {
        const type = 1;
        const input = Array.from(messages.values());
        try{
            await fetch("http:/192.168.1.188:8000/reset", {
                method : "POST",
                body : JSON.stringify({interview_type : type, input : input}),
                headers: {"Content-Type": "application/json"}
            });
        } catch(err){
            console.log("fetchData error:", err);
            showAlert('Error', 'Could not reach the server');
        } finally {
            // Empty the message map
            setMessages(new Map<string, {content : string, role : string}>());
        }
    }

    // Recording
    const {
        stopRecording,
        record,
    } = useRecorder({ws, emotion});

    return(
        <SafeAreaProvider>
            <SafeAreaView  className = 'flex-1'>
                <View className = "flex-1">
                    <WebView
                        // REPLACE WITH YOUR IPV4 (passing the elastic ip of the windows instance where the 
                        // signaling server is hosted)
                        source={{ uri: 'http:/192.168.1.188:8080/player.html?ss=ws://3.129.236.140:80' }}        
                        style={{ flex: 1 }}
                        onError={(syntheticEvent) => {
                            const { nativeEvent } = syntheticEvent;
                            console.warn('WebView error: ', nativeEvent);
                        }}
                    />
                </View>
            
                <View className = "flex-row items-center justify-stretch p-3 gap-3 bg-white">
                    <TextInput className = "grow h-12 border-2 border-gray-600 rounded-md" editable onChangeText={onChangeText} value={text} placeholder = "Type something ..."/>
                    <TouchableOpacity onPress = {sendText} >
                        <Icon name = "paper-plane" size = {24} />
                    </TouchableOpacity>

                    <TouchableOpacity onPressIn = {record} onPressOut = {stopRecording}>
                        <Icon name = "microphone" size = {24} />
                    </TouchableOpacity>

                    <TouchableOpacity onPress = {handleNew}>
                        <Icon name = "plus" size = {24} />
                    </TouchableOpacity>
                    
                    <TouchableOpacity onPress = {handleFeedback}>
                        <Icon name = "comment" size = {24} />
                    </TouchableOpacity>
                </View>
            </SafeAreaView>
        </SafeAreaProvider>
    );
}

