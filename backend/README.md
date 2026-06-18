# General

The backend is built using Python and follows the file structure of most modern ML projects. The looping pipeline of the application is the following:

Input audio from the user --> ASR (Whisper) --> Uploading txt file in backend --> NLP (OpenAI) --> TTS (Edge-TTS) --> Uploading txt file in backend --> Generation of facial animations (ArtKit) --> Avatar Rendering (MetaHumans)

After the conversation betweent the avatar and the user ends, the conversation consisting of the files in the backend, is sent to a LLM to provide feedback to the user and rate his performance, through prompt engineering techniques.

# Poetry

To enable easier dependancy management, Poetry is used. To add dependancies navigate to the backend folder and use:

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

When first cloning the application, use the following command to download all necessary commands to run the app:

   ```bash
   poetry install
   ```

All settings related to poetry can be found in file "pyproject.toml" along with "poetry.lock" (never changed by the developer).

To activate the virtual environment created by Poetry run the following and then run the command provided :

   ```bash
   poetry env activate
   ```

To update the dependancies managed by Poetry, run:

   ```bash
   poetry update
   ```