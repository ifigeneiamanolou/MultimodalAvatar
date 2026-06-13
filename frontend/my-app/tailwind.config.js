module.exports = {
  content: [
    './src/app/**/*.{js,tsx,ts,jsx}',
    './components/**/*.{js,tsx,ts,jsx}',  // add if you have this folder
  ],
  presets: [require("nativewind/preset")],
  theme: { extend: {} },
  plugins: [],
}