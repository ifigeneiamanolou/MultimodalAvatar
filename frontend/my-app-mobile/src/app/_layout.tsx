import '../../global.css';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React from 'react';

export default function RootLayout() {
  return (
    <React.Fragment>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="feedbackModal" options = {{presentation : 'modal'}} />
        {/* to delete */}
        <Stack.Screen name="feedbackTest" options = {{presentation : 'modal'}} />  
      </Stack>
      <StatusBar style = "auto"/>
    </React.Fragment>
  );
}