<div align="center">
  <img src="pycat-logo.png" alt="PyCat Logo" width="300">
</div>

# NetCat File Transfer

A simple Python GUI application for transferring files between computers using netcat.

## Features

- **Native GUI**: Built with tkinter (no external dependencies)
- **IP Detection**: Automatically detects and displays your local IP address
- **PIN Code Security**: Uses PIN codes to verify transfers
- **Network Discovery**: Discovers other instances on the network (optional)
- **Easy to Use**: Simple interface for sending and receiving files

## Requirements

- Python 3.8 or higher
- UV package manager
- netcat (`nc`) command-line tool (usually pre-installed on macOS/Linux)

## Installation

1. Install UV if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Navigate to the project directory:
```bash
cd netcat-transfer
```

3. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

4. Run the application:
```bash
uv run python netcat_transfer.py
```

Or simply:
```bash
python netcat_transfer.py
```

## Usage

### Sending a File

1. Click "Select File" to choose the file you want to send
2. Enter the receiver's IP address
3. Enter the receiver's PIN code (they should share this with you)
4. Click "Send File"

### Receiving a File

1. Share your IP address and PIN code with the sender
2. Enter the expected PIN code (should match the sender's PIN)
3. Choose a folder to save the received file (defaults to Downloads)
4. Click "Start Listening"
5. Wait for the file transfer to complete

### PIN Codes

- Each instance generates a random 6-digit PIN code
- Click "New PIN" to generate a new code
- Share your IP and PIN with the person you want to transfer files with
- The receiver should enter the sender's PIN code when starting to listen

## Network Discovery

The application automatically listens for network discovery broadcasts. When another instance is discovered, it will appear in the status log with its IP and PIN code.

## Notes

- The application uses port 12345 for file transfers
- Port 12346 is used for network discovery
- Make sure both computers are on the same network
- Firewall settings may need to allow connections on these ports

## Troubleshooting

- **"nc: command not found"**: Install netcat on your system
  - macOS: Usually pre-installed
  - Linux: `sudo apt-get install netcat` or `sudo yum install nc`
  - Windows: May need to install separately or use WSL

- **Connection refused**: Make sure the receiver has started listening before the sender initiates the transfer

- **Transfer timeout**: Large files may take longer. The timeout is set to 5 minutes by default.

