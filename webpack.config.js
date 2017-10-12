var webpack = require('webpack'),
       path = require('path');

module.exports = {

	context : __dirname + "/dev/js",
	entry : {
		app : "./app.js",
    profile_step : "./profile_step.js",
		vendor : "./vendor.js",

	},
	output: {
        path: __dirname + '/website/static/js',
        filename: '[name].bundle.js'
    },

    plugins: [
      new webpack.ProvidePlugin({
        $: "jquery",
         jQuery: "jquery",
         "window.jQuery": "jquery",
         "Tether": 'tether'
      })
  ]
};
