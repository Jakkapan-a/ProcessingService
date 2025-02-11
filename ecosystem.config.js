module.exports = {
  apps: [
    {
      name: "flask_app",
      // script: "gunicorn",
      script: "_server.py",
      // args: "-w 4 -b 0.0.0.0:10011 _server:app",
      args: "",
      // interpreter: "none",
      // interpreter: "./venv/bin/python3",
      interpreter: "./venv/Scripts/python.exe",
      watch: false,
      autorestart: false,
      instances: 1,
      max_memory_restart: "1G",
      env: {
        FLASK_ENV: "production",
        PORT: 10011
      }
    }
  ]
};
