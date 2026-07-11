This file will be used to set up a FastAPI backend server in the remote AWS EC2 instance. This will allow us to perform
heavy ML tasks in a more powerful CPU, reducing the latency of the application. The folder is build similarly to the backend folder
divided into a src and a data folder. The server is run using Uvicorn and the dependancies are managed through Poetry in the same
way as in the backend of the application.