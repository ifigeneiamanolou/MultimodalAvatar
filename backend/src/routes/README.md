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

The backend server runs using HTTP protocol (TCP when converted to a WebSocket) in "127.0.0.1" origin and port 8000. The frontend Expo server runs again using the HTTP protocol on localhost and port 8081. In case, one wants to use a different backend server URL, the corresponding variable for the WebSocket should change in the file "home.tsx" under "pages" folder In case, one wants to use a different frontend server URL, this should be reflected in the origins array used for CorsMiddleware in "main.py" under "routes" folder to avoid errors.