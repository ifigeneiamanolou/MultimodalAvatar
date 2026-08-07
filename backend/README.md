# Overview

The backend is built using Python and follows the file structure of most modern ML projects, divided in 3 main folders:
* data : stored datasets, dictionaries, and data created while running the application
* src : source code
* notebooks : contains jupyter notebooks used for testing

The src/server folder is structured into the following folders:
1) models : custom web socket manager and pydantic models
2) routes : FastAPI application, endpoints and web socket connectins
3) services : business logic used in the routes
4) utils : utilities such as a consumer-producer class based on an asyncio queue and custom buffers
The src/tests folder contains scripts to test specific parts of the application.

# Poetry

To enable easier dependancy management, Poetry is used. When first cloning the application, first ensure that pip is installed in your local environment and poetry is also installed. If not, install using poetry using pip, through:

   ```bash
   pip install poetry
   ```


Then, use the following command to download all necessary dependancies to run the app after navigating to the backend folder:

   ```bash
   poetry install
   ```
   
To add dependancies navigate to the backend folder and use:

   ```bash
   poetry add [package]
   ```

To remove a dependancy use:

   ```bash
   poetry remove [package]
   ```

To update a dependacy use:

   ```bash
   poetry update [package]
   ```

All settings related to poetry can be found in file "pyproject.toml" along with "poetry.lock" (never changed by the developer).

To activate the virtual environment created by Poetry run the following and then run the command provided :

   ```bash
   poetry env activate
   ```

# Running the server

To run the backend FastAPI server in development mode (live changes) redirect to the "routes" folder and run:

   ```bash
   fastapi dev avatar.py
   ```
or run the python script directly, using (notice you need to re-run the server when making a change with this):

   ```bash
   py avatar.py
   ```

This needs to run along with the application, so that the app runs correctly.

# Port configuration information

The backend server runs using HTTP protocol (TCP when converted to a WebSocket) in "127.0.0.1" origin and port 8000. The frontend Expo server runs again using the HTTP protocol on localhost and port 8081. In case, one wants to use a different backend server URL, the corresponding variable for the WebSocket should change in the file "home.tsx" under "pages" folder In case, one wants to use a different frontend server URL, this should be reflected in the origins array used for CorsMiddleware in "main.py" under "routes" folder to avoid CORS errors.
