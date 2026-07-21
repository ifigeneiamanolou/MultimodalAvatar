# Overview

This folder will be used to create a FastAPI application deployed through Uvicorn to run the Orpheus3B model locally, using the orpheus-speech library. This library allows us to run inference along with a SNAC decoder to produce audio waveforms instead of pure audio tokens, so that they can be used in Audio2Face. The need to isolate Orpheus3B in the Ubuntu AWS instance comes from the dependancy vllm used within orpheus-speech, to speed up inference. This supports only Linux operating systems and can be potentially installed within a Windows OS, but the process is very complicated.

# Set up instructions

To run the Uvicorn server within an AWS Ubuntu instance follow the following instructions:

1. Install poetry

2. Install python 3.11

   ```bash
   sudo apt update -y
    sudo apt install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt install python3.11
   ```
3. Go to the UbuntuServer folder inside the folder where the repo was cloned 

4.	Create and activate a virtual environment by running:

   ```bash
   poetry env use python3.11
   ```

5.	Install all dependancies 

   ```bash
   poetry install
   ```

6.	Create an .env file in the root of the repository cloned with an HF_TOKEN environment variable to avoid warnings in the next step

8.	Start the server from the UbuntuServer directory
   ```bash
   poetry run python -m src.server.routes.main
   ```
