# Introduction

The app is build using the Expo framework intended for mobile applications (iOs and Android). It is based on Typescript, along with React and tailwind css. NativeWind and react-native are used to cater for mobile application needs. To render the pixel streaming application, a web view is used, since the library pixel-streaming-frontend-ue5.8 can only be used within web applications. A pre-made frontend based on typescript is spinned up when the Expo server starts. This is fetched from the official Pixel Streaming Infrastructure
repository from Epic Games.

# Get started

1. Redirect to the folder "my-app-mobile" after cloning the repository

   ```bash
   cd frontend/my-app-mobile
   ```

2. Ensure NodeJS and npm are installed through:

   ```bash
   node --version
   npm --version
   ```

Make sure the NodeJS version is at least v18.0.0

3. Install expo

   ```bash
   npm install expo
   ```

4. Clone the epic games repository, install the necessary dependancies and build the frontend

   ```bash
   npm run setup
   ```

4. If you wish to start the frontend server in development mode, along with the web page used for pixel streaming, run:

   ```bash
   npm run dev
   ```

This will provide a QR code for the mobile app that can be used to view the mobile app.

5. To run the two servers in production mode use:

   ```bash
   npm run prod
   ```

# Frontend structure
The source code is located into the following folders:
* app : central code for all the pages of the mobile application
* constants : custom color pallette
* hooks : custom hooks (to allow recording through expo audio)

