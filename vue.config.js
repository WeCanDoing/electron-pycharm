const { defineConfig } = require('@vue/cli-service')
const NodePolyfillPlugin = require("node-polyfill-webpack-plugin"); // 引入插件

module.exports = defineConfig({
  transpileDependencies: true,
  pluginOptions: {
    electronBuilder: {
      builderOptions: {
        // 在这里指定 electron-builder 的打包选项
        asar: false,
        appId: "com.example.app",
        win: {
          target: ["nsis", "zip"]
        },
        directories: {
          output: "dist"
        },
        extraResources: [
          {
            from: "./src/pyScript/",
            to: "pyScript"
          },
          {
            from: "./src/install/",
            to: "install"
          }
        ]
      }
    }
  },
   // 其他配置...
   configureWebpack: {
    // 将 plugins 字段移动到这里
    plugins: [
      new NodePolyfillPlugin()
    ],
    resolve: {
      // 添加 fallback 字段
      fallback: {
        "fs": false, // 设置为 false 表示不使用任何 polyfill
        "child_process": false,
        "path": require.resolve("path-browserify"), // 设置为 require.resolve 表示使用指定的 polyfill 模块
        "stream": require.resolve("stream-browserify"),
        "crypto": require.resolve("crypto-browserify")
      }
    },
    
  }

})
