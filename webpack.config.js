const webpack = require('webpack');
const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    mode: 'production',
//    entry: ['core-js/stable', 'regenerator-runtime/runtime', "./assets/scripts/main.js"],
    entry: {
//        stable: 'core-js/stable',
//        runtime: 'regenerator-runtime/runtime',
//        main: ['core-js/stable', 'regenerator-runtime/runtime',"./assets/scripts/main.js"],
        admin_criterions: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/admin_criterions.js'],
        check_list: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/check_list.js'],
        criterion_pack: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/criterion_pack.js'],
        general: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/general.js'],
        login: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/login.js'],
        logs: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/logs.js'],
        one_user_info: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/one_user_info.js'],
        profile: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/profile.js'],
        results: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/results.js'],
        signup: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/signup.js'],
        upload: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/upload.js'],
        user_list: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/user_list.js'],
        version: ['core-js/stable', 'regenerator-runtime/runtime', './assets/scripts/general_imports.js', './assets/scripts/version.js'],
    },
    output: {
        path: path.join(__dirname, './src/'),
        filename: "./[name].js"
    },
    optimization: {
      splitChunks: {
        cacheGroups: {
          vendor: {
            name: 'vendors',
            test: /node_modules/,
            chunks: 'all',
            enforce: true
          }
        }
      }
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    {
                        loader: 'style-loader'
                    },
                    {
                        loader: 'css-loader'
                    }
                ]
            },
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["@babel/preset-env"]
                    }
                }
            },
            {
                test: /\.(ico)$/i,
                use: {
                    loader: 'file-loader',
                    options: {
                        name: '[name].[ext]'
                    }
                }
            }
        ]
    },
    plugins: [
        new CleanWebpackPlugin(),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        })
    ]
}
