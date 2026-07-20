# MultimodalAvatar    

This project explores how AI can be used to render conversational agents capable of epxressing emotion both through voice and facial expressions. The goal is to map dialogue to expressive facial expressions and lip sychronization, while achieving low latency using pipelines that combine speech recognition, natural language processing, speech generation and facial animation synthesis. The branch "textTotext" contains a basic connection to openai gpt-5, while the main branch "avatar" contains the whole speech-to-animation pipeline (to be merged to main). Its main folders are:

* frontend -> Build the frontend of the application via Expo
* backend -> FastAPI backend server locally running connected with the frontend
* WindowsServer -> Used in the remote AWS Windows server to host Emotion2Vec and Whisper through a Uvicorn server, as well as deploy the UE5 application with pixel streaming configured
* UbuntuServer -> Used in the remote AWS Ubuntu server to host Orpheus3B through a Uvicorn server and Audio2Face through a gRPC server