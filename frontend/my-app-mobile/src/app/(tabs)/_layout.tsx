import React from "react";
import { Tabs } from "expo-router";
import Ionicons from '@expo/vector-icons/Ionicons';
import {colors } from '../../constants/colors';
import "../../../global.css";

export default function Layout(){
    return(
        <Tabs screenOptions={{
            tabBarActiveTintColor : colors['red'],
            tabBarInactiveTintColor : colors['black'],
        }}>
            <Tabs.Screen name = "index" options={{
                'title' : 'New',
                'tabBarIcon' : ({color, focused}) => (<Ionicons name = "add-sharp" color = {focused ? colors['red'] : colors['black']} size = {24} />)
            }} />
            <Tabs.Screen name = "saved" options  = {{
                'title' : 'History',
                'tabBarIcon' : ({color, focused}) => (<Ionicons name = "calendar-outline" color = {focused ? colors['red'] : colors['black']} size = {24} />)
            }} />
            <Tabs.Screen name = "account" options = {{
                'title' : 'Account',
                'tabBarIcon' : ({color, focused}) => (<Ionicons name = "person" color = {focused ? colors['red'] : colors['black']} size = {24} />)
            }} />
        </Tabs>
    )
}