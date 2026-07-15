import { useEffect, useRef, useState } from 'react';
import React from 'react';
import {
    Config,
    AllSettings,
    PixelStreaming
} from '@epicgames-ps/lib-pixelstreamingfrontend-ue5.8';
import '../../../global.css';


export interface PixelStreamingWrapperProps {
    initialSettings?: Partial<AllSettings>;
}

export const PixelStreamingWrapper = ({
    initialSettings
}: PixelStreamingWrapperProps) => {
    // A reference to parent div element that the Pixel Streaming library attaches into
    const videoParent = useRef<HTMLDivElement>(null);

    // Pixel streaming library instance is stored into this state variable after initialization:
    const pixelStreaming = useRef<PixelStreaming | null>(null);
    
    // A boolean state variable that determines if the Click to play overlay is shown:
    const [clickToPlayVisible, setClickToPlayVisible] = useState(false);

    // A boolean state variable that determines if no WebRTC connection is shown:
    const [noConnection, setNoConnection] = useState(false);

    // Run on component mount:
    useEffect(() => {
        if (videoParent.current) {
            // Attach Pixel Streaming library to videoParent element
            const config = new Config({ initialSettings });
            const streaming = new PixelStreaming(config, {
                videoElementParent: videoParent.current         // The parent DOM element
            });
            
            // register a playStreamRejected handler to show Click to play overlay if needed
            streaming.addEventListener('playStreamRejected', () => {  // stream was rejected, redisplay click button
                setClickToPlayVisible(true);
                setNoConnection(false);
                console.log('Pixel stream rejected');
            });

            // register a webrtcconnected handler to show click every time a user loads the page
            streaming.addEventListener('webRtcConnected', () => {
                setClickToPlayVisible(true);
                console.log('Connected to signaling server');
            });

            // register a webRtcDisconnected handler to show No WebRTC connection if needed
            streaming.addEventListener('webRtcDisconnected', () => {
                setNoConnection(true);
                console.log("Disconnected from signaling server");
            });

            // register a webRtcConnecting handler to show current state on the console
            streaming.addEventListener('webRtcConnecting', () => {
                console.log("connecting ...");
            })

            // register a webRtcFailed handler to show WebRTC failed if need
            streaming.addEventListener('webRtcFailed', () => {
                setNoConnection(true);
                console.log("WebRTC connection failed");
            });

            // Save the library instance into component state so that it can be accessed later even if pixel streaming hasn't started
            pixelStreaming.current = streaming;

            // Clean up on component unmount:
            return () => {
                try {
                    streaming.disconnect();
                    pixelStreaming.current = null;
                } catch {}
            };
        }
    }, []);

    const connect = () => {
        setClickToPlayVisible(false);
    };

    return (
        <div className= 'w-full h-full relative place-content-center'>
            {noConnection ? (
                <div className = "w-full h-full place-content-center">
                    <p className = "p-6" > No WebRTC connection </p> 
                </div>
            ): (
                <>
                    {/* Mount the component */}
                    <div className = "w-full h-full" ref={videoParent}/>  

                    {clickToPlayVisible ? (
                        <div className = "w-full h-full place-content-center" onClick = {connect}>
                            <p className = 'p-6'> Click to play </p>
                        </div>
                    ) : (
                        <>
                            <div
                                className  = "absolute top-0 left-0 w-full h-full flex cursor-pointer" 
                                onClick={() => {
                                    pixelStreaming.current?.play();                 // Display the avatar
                                    setClickToPlayVisible(false);                   // Hide the click page
                                }}
                            />
                        </>
                    )}
                </>
            )}
        </div>
    );
};