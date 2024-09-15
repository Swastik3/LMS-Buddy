const path = require('path');

module.exports = {
  resolve: {
    fallback: {
      "https": require.resolve("https-browserify"),
      "https": require.resolve("stream-http"),
      "https": require.resolve("util"),
      "https": require.resolve("browserify-zlib")
    }
  },
};
