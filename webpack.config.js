var webpack = require('webpack'),
  path = require('path')

module.exports = {

  context: __dirname + '/dev/js',
  entry: {
    app: './app.js',
    profile_step: './profile_step.js',
    vendor: './vendor.js',

  },
  output: {
    path: __dirname + '/website/static/js',
    filename: '[name].bundle.js',
  },

	module: {
		rules: [
			{ test: /jquery-mousewheel/, loader: "imports-loader?define=>false&this=>window" },
			{ test: /malihu-custom-scrollbar-plugin/, loader: "imports-loader?define=>false&this=>window" }
		]
	},

  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      'window.jQuery': 'jquery',
      'Tether': 'tether',
    }),
  ],
}
