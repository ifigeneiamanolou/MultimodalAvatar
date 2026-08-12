/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/**/*.{js,jsx,ts,tsx}',
        './components/**/*.{js,jsx,ts,tsx}',
        './hooks/**/*.{js,jsx,ts,tsx}',

    ],
    presets: [require("nativewind/preset")],
    theme: {
        extend: {
            colors : {
                'red' : '#e63946',
                'honeydew' : '#f1faee',
                'steel-blue' :  '#457b9d',
                'blue' : '#a8dadc',
            }
        },
    },
    plugins: [],
};