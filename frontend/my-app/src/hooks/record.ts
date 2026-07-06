import { RefObject, useEffect, useState } from 'react';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorderState,
} from 'expo-audio';
import { Alert } from 'react-native';
import React from 'react';

type useRecorderProps = {
    ws : RefObject<WebSocket | null>;
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
    setSuccessPopUp : (show : boolean) => void;
}


export default function useRecorder({ws, setMessagePopUp, setErrorPopUp, setSuccessPopUp} : useRecorderProps){
    const [emotion, setEmotion] = useState('');
    const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
    const recorderState = useAudioRecorderState(audioRecorder);

    useEffect(() => { 
        (async () => { 
            const status = await AudioModule.getRecordingPermissionsAsync();
            if(!status.granted){
                Alert.alert('Attention', 'Permission is needed');
            }

            setAudioModeAsync({
                allowsRecording : true,
                playsInSilentMode : true,
            });
        })();
    }, []);

    const stopRecording = async () => {
        await audioRecorder.stop();
        const response = await fetch(audioRecorder.uri!);       // Extract audio from file
        const audio = await response.blob();                    // Extract raw binary audio data 

        // Encode audio
        const arrayBuffer = await audio.arrayBuffer();
        const binary = new Uint8Array(arrayBuffer);
        var base64string = btoa(String.fromCharCode(...binary));

        // Emotion recognition
        const res = await fetch("http://localhost:8000/emotion2vec", {
            method : "POST",
            body : JSON.stringify({
                model : "iic/emotion2vec_plus_seed",
                audio : base64string
            }),
            headers : {
                "Content-Type" : "application/json"
            }
        });

        // Handle the response from emotion recognition endpoint
        if(res.ok){
            const emotionData = await res.json();
            setEmotion(emotionData.data);
        } else{
            setMessagePopUp("No web socket connection found");
            setErrorPopUp(true);
            return;

        }

        // Send the recording audio for ASR through a WebSocket
        if (ws.current?.readyState !== WebSocket.OPEN){
            setMessagePopUp("No web socket connection found");
            setErrorPopUp(true);
            return;
        } else {
            ws.current?.send(base64string);
            setMessagePopUp("Audio sent");
            setSuccessPopUp(true);
        }
    };

    const record = async () => {
        await audioRecorder.prepareToRecordAsync();
        audioRecorder.record();
    };


    return {
        stopRecording,
        record,
        recorderState,
        emotion
    };
};