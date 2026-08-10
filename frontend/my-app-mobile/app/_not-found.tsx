import {View} from 'react-native';
import { Link, Stack} from 'expo-router';

export default function NotFound(){
    return(
        <>
            <Stack.Screen options = {{'title' : "404-Not Found"}}/>
            <View>
                <Link href = "/(tabs)/index">
                    Go to home page
                </Link>
            </View>
        </>
    )
}