import { Avatar } from '@readyplayerme/visage';

interface Props{
    modelSrc : string;
};

export default function AvatarComponent(props : Props){
    return(
        <Avatar modelSrc={props.modelSrc}></Avatar>
    )
};