# Remote Shutdown

## Overview
Remote Shutdown is a script made in **Python**, that sets up an HTTP server to listen for shutdown commands over the network. When a valid request is received with the correct shutdown token, the script initiates a system shutdown on the local machine.

> ℹ️ Want it in C# or as a Windows service? Check out [Remote-Shutdown](https://github.com/adamt-eng/Remote-Shutdown)!

## Features
- Remote shutdown functionality over the network.
- Token-based authorization for security.
- Simple HTTP server to listen for shutdown requests.

## Compatibility
- Windows OS

## Configuration
- `PORT_NUMBER`: The port on which the HTTP server listens.
- `TOKEN`: The token required to authorize the shutdown request.

Make sure the correct IP address and port are accessible over the network, and that the token is kept secure.

## Installation

- Clone this repository using the following command:

  ```bash
  git clone https://github.com/adamt-eng/remote-shutdown-py
  ```

- Navigate to the project directory.

- Modify `PORT_NUMBER` and `TOKEN` to your desired values.

- Run the script at-least once as administrator to ensure it can start on the next system boot.

## Usage
1. To initiate a remote shutdown, append `parameters?shutdown=true&token=<your-token>` to the URL that the script said it's listenting to requests at the first time you ran it.
  - Replace `<your-token>` with the token you previously specified in the script file.
2. If the request is valid, the machine will shut down immediately. An invalid request will return an error message.
