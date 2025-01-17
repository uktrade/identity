# identity
A dedicated service for staff profile and directory information.
Project documentation is available [here](https://uktrade.github.io/identity/).

# Setup DebugPy

Add environment variable in your .env file

    DEBUGPY_ENABLED=True

Create launch.json file inside .vscode directory

    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Remote Attach (DebugPy)",
                "type": "debugpy",
                "request": "attach",
                "connect": {
                    "host": "localhost",
                    "port": 5678
                },
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "/app/"
                    }
                ],
                "justMyCode": true
            }
        ]
    }

