# Introduction

The backend is built using Python and the FastAPI framework. WebSockets were prefered to traditional HTTP based REST APIs. This is because it enables persistent, full-duplex communication between the client and the server. This makes it more efficient for continuous data exchange between them. It provides low latency and memory overhead, since only the data is transfered from client to server and vice versa (It should be investigated whether an HTTP connection should be prefered to WebSockets in the context of this specific application).

See : https://www.geeksforgeeks.org/web-tech/what-is-web-socket-and-how-it-is-different-from-the-http/

# Running the server

To run the backend FastAPI server in development mode (live changes) redirect to the "apis" folder and run:

fastapi dev avatar.py

or run the python script directly, using (notice you need to re-run the server when making a change with this):

py avatar.py

This needs to run along with the application, so that the app runs correctly.

# Port configuration information

The backend server runs using HTTP protocol (ws when converted to a WebSocket) in "127.0.0.1" origin and port 8000. The frontend Expo server runs again using the HTTP protocol on localhost and port 8081. In case, one wants to use a different backend server URL, the corresponding variables should change in the file "index.tsx" (wsUrl, wsResponseUrl, wsAvatarUrl). In case, one wants to use a different frontend server URL, this should be reflected in the origins array used for CorsMiddleware in "avatar.py" to avoid errors.

# ASR

To perform ASR we choose to use Whisper (faster small model), which has the following advantages compared to other Whisper variants:
1. low cost (minimized using compute type int8)
2. small learning curve
3. works on both CPU and GPU
4. performs quantization for memory efficiency and speed

To note that, the ASR process would benefit greatly from using a GPU instead of the local CPU (this could potentially be achieved by redirecting it to an external server with a GPU in deployment), to reduce latency. Also, insanely-fast-whisper could be used for even faster ASR through higher throughput, but it assumes access to an NVIDIA GPU. At the same time, WhisperX provides a more complete transcription pipeline, making it useful for tasks where diarization and word-level timestamps matter. Notice it also offers support for VAD (voice activity detection) for breaking up voice properly. They all produce similar accuracies (same Whisper engine running), but differ on speed, memory use and extra features.

See: https://modal.com/blog/choosing-whisper-variants

# NLP
Currently, the fastAPI server is using the chatgpt 5.5 nano version for development purposes. During deployment, it would be better to switch to the mini version to allow for higher accuracy. Another version to consider is DeepSeek 3.2.

# TTS
ElevenLabs 2.5 flash was chosen for TTS, with the following advantages (as seen in the official site):
* low latency
* supports 32 languages 
* comparable quality to other models for the level of latency achieved

# ArtKit blendshape generation
The following pipeline is used to generate ArtKit blendshape coefficients from the audio generated after TTS, which are then applied to a MetaHuman using UE5.

1) text to phoneme conversion (using python library phonemizer)
2) viseme to ArtKit conversion using a custom conversion table

To initiallize the phonemization backend, the process takes a lot of time and is highly-ineffient, so it is initialized once on application start-up. Also, the backend used is "espeak" as it is faster and it supports multiple languages.

Potentially, facial animations could be generated with a single model, that generates ArtKit coefficients from input audio, to integrate dynamic emotion expressions. For example, Audio2Face could be used to generate 3D facial animations in real-time. This includes the sychronized motion of the tongue, jaw, lips and face skin. It is split into lip-syncing based on phonetic expressions and emotional expression from the tone of the speech. This can be used alongside Audio2Emotion to infer emotion from audio clips. The following 4 tools could be used:

1) Audio2Face SDK ==> requires an NVIDIA GPU with CUDA support, 8GB RAM, 4GB GPU memory and 10GB for the models. It supports multi-track processing, GPU acceleration through CUDA, and can be used both within Linux and Windows.
2) Audio2Face training framework ==> By training on specific characters, the models learn how to capture a desired language, personality and performance style, as well as adapt to specific terminology used in interviews through fine-tuning
3) Maya ACE Plugin ==> It provides a user interface for generating facial animations
4) UE5 plugin ==> Allows to connect animation data to any facial rig, including custom MetaHumans

OVR Lip Sync was also explored but it has been deprecated.

See : https://github.com/NVIDIA/Audio2Face-3D