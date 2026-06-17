# Introduction

The app is build using the Expo framework in order to enable both Android/ios installation and web applications. It is based on Typescript, along with React, tailwind css and nativewind to accomodate for mobile apps' appearance.

# Why React and Typescript

React is a popular Javascript library used to create reusable components for web applications, enabling interactive and dynamic websites. TypeScript that builds on Javascript by adding static data types, helping to catch mistakes early and maintain and understand code. Advantages of this setup include:

1. Enhanced type safety and early error detection
2. Improved code readability
3. Scalability for large codebases
4. Enhanced collaboration in teams
5. Known ecosystem with a lot of ressources
6. Improved maintainability (easy refactoring)

For more detail see : https://www.geeksforgeeks.org/typescript/compelling-reasons-to-use-typescript-with-react-a-developers-guide/

# Why Expo

Ecosystem of tools built around React Native, designed to help built applications both for Android/ios and the Web. It helps in initializing a project, developing up to deploying and monitoring the final application. The two main services are:

1. Expo Open-Source tools : Expo CLI for managing and creating projects, Expo Router (routing library that simplifies app navigaiton) and Expo CDK (a collection of over 75 pre-made APIs that provide access to devices like camera)

2. Expo Application Services (EAS) : helps in shipping an application (build your application, submit on Apple Store or Google Play Store and update the application with OTA updates)

See : https://www.metacto.com/blogs/what-is-expo-a-comprehensive-guide-for-mobile-app-development

# Why tailwind / nativewind

The key reasons for using tailwind are:
1. rapid prototyping through inline CSS
2. high customability
3. active community
4. easier adaptive design (various size screens, dark mode)

See : https://dev.to/codedthemes/why-is-tailwind-css-so-popular-and-is-it-worth-using-1pmf

# Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

