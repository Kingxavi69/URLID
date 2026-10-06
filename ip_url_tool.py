import argparse
import ipaddress
import json
import socket
from typing import Any
from urllib.parse import urlsplit


def classify_url_type(hostname: str | None) -> str:
    """Classify the reverse-DNS hostname returned for an IP address."""
    if not hostname:
        return "Unknown"

    host = hostname.strip().lower().rstrip(".")
    if not host:
        return "Unknown"

    if any(keyword in host for keyword in ["mail", "mx", "smtp", "imap", "pop"]):
        return "Mail server"

    if any(keyword in host for keyword in ["api", "gateway", "service", "rest", "rpc"]):
        return "API"

    if any(keyword in host for keyword in ["cdn", "cache", "static", "assets", "media", "edge", "content"]):
        return "CDN / static content"

    if any(
        keyword in host
        for keyword in [
            "aws",
            "azure",
            "googlecloud",
            "cloudflare",
            "digitalocean",
            "amazonaws",
            "vercel",
            "netlify",
            "heroku",
            "linode",
        ]
    ):
        return "Cloud / hosted service"

    if host.startswith("www") or "." in host:
        return "Website"

    return "Unknown"


def resolve_ip_url(ip_address: str) -> dict[str, Any]:
    """Resolve an IP address to a hostname and classify the host type."""
    ip = ip_address.strip()
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        url = hostname.strip().rstrip(".")
        return {
            "ip": ip,
            "url": url,
            "type": classify_url_type(url),
            "status": "resolved",
        }
    except (socket.herror, socket.gaierror, OSError):
        return {
            "ip": ip,
            "url": None,
            "type": "Unknown",
            "status": "unresolved",
        }


def resolve_url(url: str) -> dict[str, Any]:
    """Resolve a URL's hostname to IP addresses and classify its host."""
    value = url.strip()
    candidate = value if "://" in value else f"//{value}"
    try:
        parsed = urlsplit(candidate)
        hostname = parsed.hostname
        if not hostname or parsed.username or parsed.password:
            raise ValueError
        if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError
    except ValueError:
        return {
            "url": value,
            "host": None,
            "ips": [],
            "type": "Unknown",
            "status": "invalid",
        }

    try:
        records = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        addresses = list(dict.fromkeys(record[4][0] for record in records))
        if not addresses:
            raise socket.gaierror("No addresses returned")
    except (socket.gaierror, OSError):
        return {
            "url": value,
            "host": hostname,
            "ips": [],
            "type": classify_url_type(hostname),
            "status": "unresolved",
        }

    try:
        ipaddress.ip_address(hostname)
        url_type = "IP address"
    except ValueError:
        url_type = classify_url_type(hostname)

    return {
        "url": value,
        "host": hostname,
        "ips": addresses,
        "type": url_type,
        "status": "resolved",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve a URL to IP addresses, or an IP address to its hostname."
    )
    parser.add_argument("target", help="URL, domain name, or IPv4/IPv6 address to inspect")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the result as JSON instead of a readable summary",
    )
    args = parser.parse_args()

    try:
        ipaddress.ip_address(args.target)
        result = resolve_ip_url(args.target)
        result["ips"] = [result["ip"]]
    except ValueError:
        result = resolve_url(args.target)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if "ip" in result and result["status"] == "resolved":
        print(f"IP Address: {result['ip']}")
        print(f"Resolved URL: {result['url']}")
        print(f"URL Type: {result['type']}")
    elif result["status"] == "resolved":
        print(f"URL: {result['url']}")
        print(f"Host: {result['host']}")
        print(f"IP Address(es): {', '.join(result['ips'])}")
        print(f"URL Type: {result['type']}")
    else:
        print(f"URL/IP: {result.get('url', result.get('ip'))}")
        print(f"Host: {result.get('host') or 'None'}")
        print(f"URL Type: {result['type']}")
        print(f"Status: {result['status']}")


if __name__ == "__main__":
    main()
