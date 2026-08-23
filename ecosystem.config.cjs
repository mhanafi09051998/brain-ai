module.exports = {
  apps: [
    {
      name: "9router",
      script: "C:/ProgramData/npm/node_modules/9router/app/server.js",
      cwd: "C:/ProgramData/npm/node_modules/9router/app",
      env: {
        PORT: 20128,
        HOSTNAME: "0.0.0.0",
        NODE_ENV: "production",
        INITIAL_PASSWORD: process.env.INITIAL_PASSWORD || "change_this_password"
      }
    }
  ]
};

