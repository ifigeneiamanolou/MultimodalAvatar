# General

The backend is built using Python and follows the file structure of most modern ML projects, divided in 3 main folders:
* data : stored datasets, dictionaries, and data created while running the application
* src : source code
* notebooks : contains jupyter notebooks

The src folder is structured into the following folders:
1) models : custom classes and pydantic models
2) routes : FastAPI application, endpoints and web socket connectins
3) services : business logic used in the routes
4) tests : test scripts to evaluate the performance of specific parts of the app
5) utils : utilities such as hashing and authentication

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

For information on running the FastAPI backend server, go to the README in the "backend/src/routes" folder.

# Additional installations needed
Currently, to generate ArtKit coefficients, phonemization is used, planning to migrate to Audio2Face in the future. The backend used for this is "espeak" and needs to be installed. To do this, we need to download "msi" file through this github page :
https://github.com/espeak-ng/espeak-ng/releases, and run the installer following the default options.

Also, ffmpeg needs to installed through the official site: https://www.gyan.dev/ffmpeg/builds/ or the githu releases page. Make sure the installed version is 4, 5, 6 or 7 for litorchcodec to work properly and that the "shared" zip is downloaded. Afterwards, the zip needs to be extracted and the directory to the bin folder added to "whisper.py" in the location shown.
