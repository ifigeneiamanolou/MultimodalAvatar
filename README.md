# Overview   

This branch contains an alternative to the pipeline proposed in the main branch with the speech to speech model from open router used along with Audio2Face. The main folders are:

* frontend -> Build the frontend of the application via Expo
* backend -> FastAPI backend server locally running connected with the frontend
* WindowsServer -> FastAPI server used to deploy Whisper on a windows EC2 instance

# Developer instructions
To locally start contributing to this branch the following components need to be set up:
1. AWS Windows EC2 instance with Signaling server with a CoTURN implementation, a packaged UE5 application, and the uvicorn server running
3. Expo server running locally
4. Uvicorn central backend server running locally

Instructions on how to set up the uvicorn and the expo servers, as well as how to configure the EC2 instance, can be found in the READMEs of the corresponding folders in this repository. Also, instructions on how to set up the signaling server, the gRPC Audio2Face server and the packaged UE5 application can be found in the README of the "MultimodalAvatarUE5" repository.

## Running the application
For all the parts to be connected properly, the developer should make sure that the UE5 has started pixel streaming before the backend central server is spinned up so that a web socket connection
is established properly between them.