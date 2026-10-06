# IP URL Disclosure Tool

This project contains a lightweight Python utility that resolves a URL or domain to its IPv4/IPv6 address(es), and labels the host as a website, API, mail server, cloud service, CDN/static host, or IP address. It also supports reverse-DNS lookups for IP addresses.

## Usage

```bash
python ip_url_tool.py https://api.example.com/v1
```

Example output:

```text
URL: https://api.example.com/v1
Host: api.example.com
IP Address(es): 203.0.113.10
URL Type: API
```

A bare domain works too, and IPv4/IPv6 addresses still perform reverse-DNS lookups:

```bash
python ip_url_tool.py example.com
python ip_url_tool.py 8.8.8.8
```

JSON output:

```bash
python ip_url_tool.py https://api.example.com/v1 --json
```

## Web interface

Run the local web interface with Python 3.10 or newer:

```bash
python3 web_server.py
```

Open `http://127.0.0.1:8000` in a browser. The server binds to localhost by default. To select a different local port, use `python3 web_server.py --port 8080`.

## Notes

- Forward and reverse DNS lookups use Python's standard `socket` library.
- URL type is inferred from hostname conventions, not from the remote website's content or ownership.
- DNS results can vary by network, resolver, and time.
