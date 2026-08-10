# MultimodalAvatar    

This project explores how AI can be used to render conversational agents capable of epxressing emotion both through voice and facial expressions. The goal is to map dialogue to expressive facial expressions and lip sychronization, while achieving low latency using pipelines that combine speech recognition, natural language processing, speech generation and facial animation synthesis. The branch "textTotext" contains a basic connection to openai gpt-5, while the main branch contains the whole speech-to-animation pipeline. Its main folders are:

* frontend -> Build the frontend of the application via Expo
* backend -> FastAPI backend server locally running connected with the frontend
* WindowsServer -> Used in the remote AWS Windows server to host Emotion2Vec, Distilert Whisper through a Uvicorn server
* UbuntuServer -> Used in the remote AWS Ubuntu server to host Orpheus3B through a Uvicorn server


## Third-party code

This project includes modified portions of Oprheus-TTS (https://github.com/canopyai/Orpheus-TTS.git). The following files are based on this repository:
* UbuntuServer/src/server/services/decoder.py
* UbuntuServer/src/server/services/engine_class.py

Original code is Copyright © canopylabs.ai. Licensed under the Apache License 2.0.


# Developer instructions
To locally start contributing to the repository the following components need to be set up:
1. AWS Windows EC2 instance with Uvicorn server, Signaling server with a CoTURN implementation and a packaged UE5 application
2. AWS Ubuntu EC2 instance with Uvicorn server and gRPC Audio2Face server
3. Expo server running locally
4. Uvicorn central backend server running locally
Instructions on how to set up the uvicorn and the expo servers, as well as how to configure the EC2 instances, can be found in the READMEs of the corresponding folders in this repository. Also, instructions on how to set up the signaling server, the gRPC Audio2Face server and the packaged UE5 application can be found in the README of the "MultimodalAvatarUE5" repository.

## Running the application
For all the parts to be connected properly, the developer should make sure that the UE5 has started pixel streaming before the backend central server is spinned up so that a web socket connection
is established properly between them.