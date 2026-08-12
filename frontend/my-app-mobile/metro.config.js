const path = require('path');
const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

config.resolver.blockList = [
  new RegExp(`${path.resolve(__dirname, 'PixelStreamingInfrastructure').replace(/\\/g, '\\\\')}.*`),
];

module.exports = withNativeWind(config, { input:  './global.css' });