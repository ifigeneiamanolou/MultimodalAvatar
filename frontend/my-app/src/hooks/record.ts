import { Dispatch, RefObject, SetStateAction, useEffect, useState } from 'react';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorderState,
} from 'expo-audio';
import { Alert } from 'react-native';

type useRecorderProps = {
    ws : RefObject<WebSocket | null>;
    setMessagePopUp : (message : string) => void;
    setErrorPopUp : (show : boolean) => void;
    setSuccessPopUp : (show : boolean) => void;
    emotion : RefObject<string>;
    setAudio : (audio : any) => void;
}


export default function useRecorder({ws, setMessagePopUp, setErrorPopUp, setSuccessPopUp, emotion, setAudio} : useRecorderProps){
    const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
    const recorderState = useAudioRecorderState(audioRecorder);

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
        const arrayBuffer = await audio.arrayBuffer();
        const binary = new Uint8Array(arrayBuffer);
        var base64string = btoa(String.fromCharCode(...binary));

        // Fill in the audio to be used for playback by the user
        setAudio(arrayBuffer);

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
                setMessagePopUp("Error during emotion recognition");
                setErrorPopUp(true);
                return;
            }
        } catch (e){
            setMessagePopUp("Error connecting to the Windows server");
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
        recorderState
    };
};