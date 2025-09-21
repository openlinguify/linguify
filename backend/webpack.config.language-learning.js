const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = (env, argv) => {
  const mode = argv.mode || 'development';
  const isDev = mode === 'development';

  return {
    mode: mode,
    entry: './apps/language_learning/static/language_learning/src/main.js',
    output: {
      path: path.resolve(__dirname, 'apps/language_learning/static/language_learning/dist'),
      filename: 'language-learning.bundle.js',
      clean: true
    },
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader'
          }
        },
        {
          test: /\.(scss|sass|css)$/,
          use: [
            isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
            'css-loader',
            'sass-loader'
          ]
        },
        {
          test: /\.xml$/,
          type: 'asset/source'
        }
      ]
    },
    resolve: {
      extensions: ['.js', '.jsx'],
      alias: {
        '@language-learning': path.resolve(__dirname, 'apps/language_learning/static/language_learning/src')
      }
    },
    plugins: [
      ...(!isDev ? [new MiniCssExtractPlugin({
        filename: 'language-learning.bundle.css'
      })] : [])
    ],
    devtool: isDev ? 'source-map' : false,
    watchOptions: {
      ignored: /node_modules/
    }
  };
};