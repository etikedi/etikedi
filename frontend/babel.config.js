module.exports = {
    presets: ["@vue/cli-plugin-babel/preset"],
    devServer: {port: 5000, proxy: "127.0.0.1/api"}
};
