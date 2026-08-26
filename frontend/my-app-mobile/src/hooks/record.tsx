import {useEffect} from 'react';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
} from 'expo-audio';
import { Alert } from 'react-native';

const showAlert = (title : string, message : string) => {
    Alert.alert(
      title,
      message,
      [
        { text: "OK", onPress: () => console.log("OK Pressed") }
      ]
    );
};

export default function useRecorder(){
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
        const base64string : string = await new Promise((resolve, reject) => {
            const reader = new window.FileReader();
            reader.onloadend = () => {
                if(reader.result){
                    const base64 = reader.result.toString();        
                    resolve(base64.split(',')[1]);
                } else{
                    reject(new Error('File reader produced no result'));
                }
            }
            reader.onerror = reject;
            reader.readAsDataURL(audio); 
        });
    
        return base64string;
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