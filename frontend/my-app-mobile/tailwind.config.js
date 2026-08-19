/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}"
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