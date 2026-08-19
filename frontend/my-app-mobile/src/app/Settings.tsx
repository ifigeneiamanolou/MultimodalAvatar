import {View, Text, Modal, NativeSyntheticEvent, TouchableOpacity, Switch} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import React from 'react';
import { colors } from '../constants/colors';

type props = {
    visible : boolean;
    dismiss : (event : NativeSyntheticEvent<any>) => any;
    setInterviewer : (type : boolean) => any;
    interviewer : boolean
};

export default function Settings({ visible, dismiss, setInterviewer, interviewer} : props) {
    const toggleSwitch = () => setInterviewer(!interviewer);

    return(
        <Modal visible={visible} transparent animationType='fade' onRequestClose={dismiss} >
            {/* Full screen transparent component */}
            <View className = "flex-1" >
                {/* Settings box */}
                <View className = "absolute rounded-lg p-4 bg-gray-300"
                    style={{
                        top: 150,
                        right: 10,
                        width: 150,
                }}>
                    {/* Header */}
                    <View className='flex-row items-center justify-between'>
                        <Text className='text-lg font-bold' style = {{fontWeight : 'bold'}}>
                            Settings
                        </Text>

                        <TouchableOpacity onPress = {dismiss}>
                            <Icon name = "times" size  = {24} color = "black" />
                        </TouchableOpacity>
                    </View>

                    {/* Interviewer switch */}
                    <View className="flex-row items-center justify-between">
                        <Switch 
                            trackColor={{false: '#767577', true: colors['blue']}}
                            thumbColor={interviewer? colors['dark_blue'] : '#f4f3f4'}
                            ios_backgroundColor="#3e3e3e"
                            onValueChange={toggleSwitch}
                            value={interviewer}
                        />
                        <Text className='text-base'> 
                            {interviewer ? "Interviewer" : "Interviewee"}
                        </Text> 
                    </View>
                </View>
            </View>
        </Modal>
    );
};