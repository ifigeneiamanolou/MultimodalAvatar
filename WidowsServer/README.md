# Overview

This folder will be used to set up a FastAPI backend server in the remote AWS EC2 Windows instance. This will allow us to perform
heavy ML tasks in a more powerful GPU, reducing the latency of the application. The folder is build similarly to the backend folder divided into a src and a data folder. The server is run using Uvicorn and the dependancies are managed through Poetry. To start the server or manage dependancies, the procedure is the same as the one described in the README of the backend folder.