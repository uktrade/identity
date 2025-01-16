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
                "type": "python",
                "request": "attach",
                "port": 5678,
                "host": "localhost",
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "/app/"
                    }
                ],
                "justMyCode": true
            },
        ]
    }
