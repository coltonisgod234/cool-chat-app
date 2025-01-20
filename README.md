# Cool Chat App

A simple real-time chat application built with Python Flask and vanilla JavaScript.

## Features
- User authentication
- Real-time messaging
- Channel-based communication
- Permission system

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up SSL certificates in the `ssl/` directory:
   - `server.crt`
   - `server.key`

4. Create required CSV files:
   ```bash
   touch sessions.csv users.csv
   ```

5. Start the server:
   ```bash
   python network.py
   ```

6. Access the application at `https://localhost:443`

## SSL Certificate for Development

To generate a self-signed SSL certificate, run the following script:

1. Make the script executable:
   ```bash
   chmod +x setup.sh
   ```

2. Run the script:
   ```bash
   ./setup.sh
   ```

This will create an `ssl/` directory and generate a self-signed certificate (`server.crt`) and a private key (`server.key`) for local development.

**Note:** This is for development only. Do not use in production.

## License
GNU General Public License v3.0

See LICENSE file for details.