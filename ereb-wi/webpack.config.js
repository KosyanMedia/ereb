module.exports = {
    entry: "./entry.js",
    output: {
        path: "./build",
        publicPath: "/build/",
        filename: "bundle.js"
    },
    module: {
        loaders: [
            { test: /\.css$/, loader: "style!css" },
            { test: /\.woff$/,   loader: "url-loader?limit=10000&mimetype=application/font-woff" },
            { test: /\.woff2$/,   loader: "url-loader?limit=10000&mimetype=application/font-woff2" },
            { test: /\.ttf$/,    loader: "file-loader" },
            { test: /\.eot$/,    loader: "file-loader" },
            { test: /\.svg$/,    loader: "file-loader" },
            { test: /\.coffee$/, loader: "coffee-loader" },
            { test: /\.scss$/, loader: "style!css!sass?sourceMap" }
        ]
    }
};
