# Kali Linux Installation Guide

This guide installs and runs the URL IP disclosure tool on Kali Linux. The tool uses only the Python standard library; no Python packages or virtual environment are required.

## Requirements

- Kali Linux with network access
- Python 3.10 or newer
- Git

## Install

Open a terminal and install Python and Git if needed:

```bash
sudo apt update
sudo apt install -y python3 git
```

Check the Python version:

```bash
python3 --version
```

The version must be 3.10 or newer. Clone the repository and enter its directory:

```bash
git clone https://github.com/Kingxavi69/URLID.git
cd URLID
```

## Run

Resolve a full URL:

```bash
python3 ip_url_tool.py "https://api.example.com/v1"
```

Resolve a bare domain:

```bash
python3 ip_url_tool.py example.com
```

Look up the reverse-DNS hostname for an IP address:

```bash
python3 ip_url_tool.py 8.8.8.8
```

Print the result as JSON:

```bash
python3 ip_url_tool.py "https://api.example.com/v1" --json
```

Launch the local web interface:

```bash
python3 web_server.py
```

Then open `http://127.0.0.1:8000` in a browser. Stop the server with `Ctrl+C`.

## Troubleshooting

- If `python3` is not found, install it with `sudo apt install python3`.
- If the tool reports an unresolved host, check the URL or domain and confirm Kali has network and DNS access. DNS answers depend on the network's resolver.
- Run the tool as your normal user; `sudo` is not needed.
