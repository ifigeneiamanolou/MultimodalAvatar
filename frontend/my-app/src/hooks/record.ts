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
    setAudio : (audio : any) => void;
}

export default function useRecorder({ setAudio} : useRecorderProps){
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

        return base64string;
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