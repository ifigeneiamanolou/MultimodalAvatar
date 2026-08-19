import React from "react";
import { useLocalSearchParams } from 'expo-router';
import {View, ScrollView, TouchableOpacity, Dimensions} from 'react-native';
import ReactMarkDown from 'react-native-markdown-display';
import '../../global.css';
import Icon from 'react-native-vector-icons/FontAwesome';
import {showAlert} from './(tabs)/index';
import uuid from "react-native-uuid";
import constants from '@/src/constants/app';

export default function Feedback(){
    var {feedback} = useLocalSearchParams<{feedback : string}>();
    const {messages} = useLocalSearchParams<{messages : string}>();
    const {interviewer} = useLocalSearchParams();

    const dedent = (str: string) =>
        str.split('\n').map(line => line.trimStart()).join('\n');

    // Store in a db for future use
    const save = async () => {
        if(feedback === "" || feedback === null || feedback === undefined){
            showAlert('Error', 'Wait for the LLM to respond');
            return;
        }

        // Simulate a random user
        const id = uuid.v4();
        try{
            await fetch(`${constants.BACKEND_SERVER_URL}/feedback/database`, {
                method : "POST",
                body : JSON.stringify({
                    messages : messages, 
                    interview_type : interviewer,
                    id : id,
                    feedback : feedback
                }),
                headers: {"Content-Type": "application/json"}
            });
        } catch (err){
            console.log("fetchData error:", err);
            showAlert('Error', 'Could not reach the server');
            return;
        }  
    };

    // Download locally in the mobile device
    const download = () => {
        if(feedback === "" || feedback === null || feedback === undefined){
            showAlert('Error', 'Wait for the LLM to respond');
            return;
        }

        // Create a blob object of mime type text and attach to a temporary anchor element, triggered programmatically
        const element = document.createElement("a");
        const file = new Blob([feedback], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = "myFeedback.txt";
        document.body.appendChild(element); // Required for this to work in FireFox
        element.click();
    };

    // Generate again the feedback
    const generateAgain = async () => {
        if(feedback === "" || feedback === null || feedback === undefined){
            showAlert('Error', 'Wait for the LLM to respond');
            return;
        }

        var response = "";
        try{
            const res = await fetch(`${constants.BACKEND_SERVER_URL}/feedback`, {
                method : "POST",
                body : JSON.stringify({input : messages, interview_type : interviewer}),
                headers: {"Content-Type": "application/json"}
            });

            response = await res.json();
        } catch (err){
            console.log("fetchData error:", err);
            showAlert('Error', 'Could not reach the server');
            return;
        }  

        feedback = response.toString();
    };

    const screenHeight = Dimensions.get('window').height

    return(
        <View style = {{height : screenHeight * 0.9}} className = "bg-white">
            <View className = "flex-1 bg-gray-100 border-gray-300 border-2 rounded-lg p-4 m-8"> 
                <ScrollView
                    contentInsetAdjustmentBehavior="automatic"
                    persistentScrollbar
                    scrollIndicatorInsets={{top : 10, left : 0, right : 0, bottom : 10}}
                    contentContainerStyle={{ paddingRight: 20 }}
                >
                    <View className='flex-1'>
                        <ReactMarkDown>
                            {dedent(feedback)}
                        </ReactMarkDown>
                    </View>
                </ScrollView>
            </View>

            <View className = "flex flex-row justify-between mx-10 mb-8">
                <TouchableOpacity onPress={download} className='p-2'>
                    <Icon name = "download" size = {24} color = "black"/>
                </TouchableOpacity>

                <TouchableOpacity onPress={save} className='p-2'>
                    <Icon name = "save" size = {24} color = "black"/>
                </TouchableOpacity>

                <TouchableOpacity onPress={generateAgain} className='p-2'>
                    <Icon name = "rotate-right" size = {24} color = "black"/>
                </TouchableOpacity>
            </View>
        </View>
    );
}