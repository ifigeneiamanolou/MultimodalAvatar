import React, { useEffect, useRef, useState } from 'react';
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
    const [pixelStreaming, setPixelStreaming] = useState<PixelStreaming>();
    
    // A boolean state variable that determines if the Click to play overlay is shown:
    const [clickToPlayVisible, setClickToPlayVisible] = useState(false);

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
            });

            // Save the library instance into component state so that it can be accessed later even if pixel streaming hasn't started
            setPixelStreaming(streaming);

            // Clean up on component unmount:
            return () => {
                try {
                    streaming.disconnect();
                } catch {}
            };
        }
    }, []);

    return (
        <div className= 'w-full h-full relative'>
            {/* DOM element to render pixel streaming */}
            <div className = "w-full h-full" ref={videoParent}/>   
            {/* Alternative content */}     
            {clickToPlayVisible && (
                <div
                    className  = "top-0 left-0 w-full h-full flex justify-center align-middle cursor-pointer" 
                    onClick={() => {
                        pixelStreaming?.play();                 // Display the avatar
                        setClickToPlayVisible(false);           // Hide the click page
                    }}
                >
                    <div>Click to play</div>
                </div>
            )}
        </div>
    );
};