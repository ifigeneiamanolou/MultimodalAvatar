import { RefObject, useEffect } from 'react';
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
        const url = URL.createObjectURL(audio);

        // Send the recording audio for ASR through a WebSocket
        if (ws.current?.readyState !== WebSocket.OPEN){
          setMessagePopUp("No web socket connection found");
          setErrorPopUp(true);
        } else {
          ws.current?.send(audio);
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
    };
};