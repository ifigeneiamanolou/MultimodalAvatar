import { RefObject, useEffect} from 'react';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorderState,
} from 'expo-audio';
import { Alert } from 'react-native';

type useRecorderProps = {
    ws : RefObject<WebSocket | null>;           // Web socket connection with whisper
    emotion : RefObject<string>;                // emotion label from emotion2vec
}

const showAlert = (title : string, message : string) => {
    Alert.alert(
      title,
      message,
      [
        { text: "OK", onPress: () => console.log("OK Pressed") }
      ]
    );
};


export default function useRecorder({ws, emotion} : useRecorderProps){
    const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);

    useEffect(() => { 
        (async () => { 
            const status = await AudioModule.getRecordingPermissionsAsync();
            if(!status.granted){
                const request = await AudioModule.requestRecordingPermissionsAsync();
                if(!request.granted){
                    Alert.alert('Attention', 'Permission is needed');
                }
            }

            await setAudioModeAsync({
                allowsRecording : true,
                playsInSilentMode : true,
            });
        })();
    }, []);

    const stopRecording = async () => {
        await audioRecorder.stop();
        const response = await fetch(audioRecorder.uri!);       // Extract audio from file
        const audio = await response.blob();                    // Extract raw binary audio data 

        // Encode audio into a base64 string
        const array = await audio.arrayBuffer();
        const binary = new Uint8Array(array);
        var base64string = btoa(String.fromCharCode(...binary));

        // Emotion recognition
        try{
            const res = await fetch("http://3.129.236.140:8000/emotion2vec", {              // Elastic IP address 
                method : "POST",
                body : JSON.stringify({
                    model : "iic/emotion2vec_plus_seed",
                    audio : base64string,
                    language : "en",
                }),
                headers : {
                    "Content-Type" : "application/json"
                }
            });

            // Handle the response from emotion recognition endpoint
            if(res.ok){
                const emotionData = await res.json();
                emotion.current = emotionData.data;
            } else{
                console.log('Error during emotion recognition with status %s', res.status);
                showAlert('Error', 'Error during emotion recognition');
            }
        } catch (e){
            console.log('Error connecting to the windows server : %s', e);
            showAlert('Error', 'Windows server connection issue');
        }

        // Send the recording audio for ASR through a WebSocket
        if (ws.current?.readyState !== WebSocket.OPEN){
            showAlert('Error', 'Web socket is closed');
        } else{
            ws.current?.send(base64string);
            console.log('audio sent to a2f');
        }
    };

    const record = async () => {
        await audioRecorder.prepareToRecordAsync();
        audioRecorder.record();
    };

    return {
        stopRecording,
        record
    };
};