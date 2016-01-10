var path = require('path');
var webpack = require('webpack');
var HTML = require('html-webpack-plugin');

module.exports = {
    entry: './scripts/main.js',
    output: {
        path: path.join(__dirname, 'dist/'),
        filename: 'algebra-calc.min.js',
        sourceMapFilename: '[file].map',
        publicPath: '/',
        jsonpFunction: 'wpload'
    },
    module: {
        loaders: [
            {
                test: /\.css$/, loader: 'style!css'
            },
            {
                test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/font-woff"
            },
            {
                test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/font-woff"
            },
            {
                test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/octet-stream"
            },
            {
                test: /\.otf(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/octet-stream"
            },
            {
                test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
                loader: "file"
            },
            {
                test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=image/svg+xml"
            },
            {
                test: /\.(jpe?g|png|gif|svg|ico)$/i,
                loaders: [
                    'file?hash=sha512&digest=hex&name=[hash].[ext]',
                    'image-webpack?bypassOnDebug&optimizationLevel=7&interlaced=false'
                ]
            }
        ]
    },
    devtool: 'source-map',
    plugins: [
        new webpack.optimize.UglifyJsPlugin()
    ],
    plugins: [
        new HTML({
            template: 'index.html',
            inject: 'body'
        })
    ]
};
