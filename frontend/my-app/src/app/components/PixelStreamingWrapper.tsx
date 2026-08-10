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

    // Run on component mount:
    useEffect(() => {
        if (videoParent.current) {
            // Attach Pixel Streaming library to videoParent element
            const config = new Config({ initialSettings });
            const streaming = new PixelStreaming(config, {
                videoElementParent: videoParent.current         // The parent DOM element
            });
            pixelStreaming.current = streaming;
            
            // register a playStreamRejected handler to show Click to play overlay if needed
            streaming.addEventListener('playStreamRejected', () => {  // stream was rejected, redisplay click button
                console.log('PLAY STREAM REJECTED');
            });

            // register a webrtcconnected handler to show click every time a user loads the page
            streaming.addEventListener('webRtcConnected', () => {
                console.log('STREAM REJECTED');
            });

            // register a webRtcDisconnected handler to show No WebRTC connection if needed
            streaming.addEventListener('webRtcDisconnected', () => {
                console.log('DISCONNECTED');
            });

            // register a webRtcConnecting handler to show current state on the console
            streaming.addEventListener('webRtcConnecting', () => {
                console.log('CONNECTING');
            })

            // register a webRtcFailed handler to show WebRTC failed if need
            streaming.addEventListener('webRtcFailed', () => {
                console.log('FAILED');
                
            });

            // Start the stream
            pixelStreaming.current.play();

            // Clean up on component unmount:
            return () => {
                try {
                    streaming.disconnect();
                } catch (error){
                    console.log(error);
                } finally {
                    pixelStreaming.current = null;
                }
            };
        }
    }, [initialSettings]);

    return (
        <div className="relative w-full h-full">
            <div ref={videoParent} className="w-full h-full"/>
        </div>
    );
};