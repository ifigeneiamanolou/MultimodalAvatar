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