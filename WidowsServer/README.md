# Overview

This folder will be used to set up a FastAPI backend server in the remote AWS EC2 Windows instance. This will allow us to perform
heavy ML tasks in a more powerful GPU, reducing the latency of the application. The folder is build similarly to the backend folder divided into a src and a data folder. The server is run using Uvicorn and the dependancies are managed through Poetry. 

# Developer Instructions
To start the server or manage dependancies, the procedure is the same as the one described in the README of the backend folder.

1. Install poetry
2. Activate a poetry virtual environment
3. Install the dependancies
4. Create an .env file with an HF_TOKEN key
5. Run the python script main.py

Before doing the above ensure the server is deployed on a machine with a GPU and CUDA drivers installed. These can be installed using this link https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local. Afterwards, find the location of the cuda drivers inside Program files and copy the path of 
the bin folder to the environment variables.