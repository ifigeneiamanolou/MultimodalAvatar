import React from "react";

interface Props{
    modelSrc : string;
};

export default function AvatarComponent(props : Props){
    // Fallback for Android and ios

    return(
        <div>
            <p> No 3D character available </p>
        </div>
    );
};