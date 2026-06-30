import React, { useEffect, useRef } from "react";
// Default error popup from tailwind : https://v1.tailwindcss.com/components/alerts

interface Props{
    showPopup : boolean,
    closePopup : Function,
    message : string
}

export default function Alert({showPopup, closePopup, message} : Props){
    const popupRef = useRef(null);
    const timerId = useRef<number>(null);

    useEffect(() => {
        if (showPopup) {
            //Creating a timeout
            timerId.current = setTimeout(() => {
                closePopup()
            }, 5000);       // Wait 5000 ms until closing the popup
        }

        return () => {
            //Clearing a timeout
            clearTimeout(timerId.current);
        };
    }, [showPopup]);

    if(!showPopup){return null}

    return(
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className ="font-bold block">Attention! </strong>
            <span className ="block w-full sm:inline pr-8">{message}</span>
            <span className ="absolute top-0 right-0 px-4 py-3">
                <svg className ="fill-current h-6 w-6 text-red-500" role="button" onClick = {() => closePopup()} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/></svg>
            </span>
        </div>
    );
}