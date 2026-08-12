# Introduction

The app is build using the Expo framework intended for web applications. It is based on Typescript, along with React and tailwind css.

# Get started

1. Redirect to the folder "my-app" after cloning the repository

   ```bash
   cd frontend/my-app
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

4. Install dependencies specific to the project

   ```bash
   npm install
   ```

4. If you wish to start the frontend server in development mode, run the following:

   ```bash
   npx expo start
   ```

This will also provide a QR code for the mobile app but the mobile app is supported by the Expo app "my-app-mobile".

# Frontend structure
The source code is located into the "src" folder, which is divided into the "app" folder and the "hooks" folder. The first one contains all the pages ("pages" folder) and the components used in them ("components" folder), like pop ups. The second one contains importable functions, that do not render content, but are used from the pages and the components, to improve readability.

