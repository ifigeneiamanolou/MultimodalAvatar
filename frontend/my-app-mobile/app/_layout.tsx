import '../global.css';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="feedbackModal" options = {{presentation : 'modal'}} />
      </Stack>
      <StatusBar style = "dark"/>
    </>
  );
}