import socket

from ip_url_tool import classify_url_type, resolve_ip_url, resolve_url
from web_server import lookup_target


def test_classify_web_url():
    assert classify_url_type("www.example.com") == "Website"
    assert classify_url_type("api.example.com") == "API"
    assert classify_url_type("mail.example.com") == "Mail server"
    assert classify_url_type("cdn.example.com") == "CDN / static content"
    assert classify_url_type("aws.amazon.com") == "Cloud / hosted service"


def test_resolve_ip_url_success(monkeypatch):
    def fake_gethostbyaddr(ip):
        assert ip == "8.8.8.8"
        return ("dns.google", [], ["8.8.8.8"])

    monkeypatch.setattr(socket, "gethostbyaddr", fake_gethostbyaddr)
    result = resolve_ip_url("8.8.8.8")

    assert result["ip"] == "8.8.8.8"
    assert result["url"] == "dns.google"
    assert result["type"] == "Website"
    assert result["status"] == "resolved"


def test_resolve_ip_url_failure(monkeypatch):
    def fake_gethostbyaddr(ip):
        raise socket.herror("No address associated with hostname")

    monkeypatch.setattr(socket, "gethostbyaddr", fake_gethostbyaddr)
    result = resolve_ip_url("203.0.113.10")

    assert result["ip"] == "203.0.113.10"
    assert result["url"] is None
    assert result["type"] == "Unknown"
    assert result["status"] == "unresolved"


def test_resolve_url_success(monkeypatch):
    def fake_getaddrinfo(host, port, type):
        assert host == "api.example.com"
        assert port is None
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.10", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.11", 0)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    result = resolve_url("https://api.example.com/v1")

    assert result["url"] == "https://api.example.com/v1"
    assert result["host"] == "api.example.com"
    assert result["ips"] == ["192.0.2.10", "192.0.2.11"]
    assert result["type"] == "API"
    assert result["status"] == "resolved"


def test_resolve_url_accepts_bare_domain(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.20", 0))
        ],
    )

    result = resolve_url("example.com/path")

    assert result["host"] == "example.com"
    assert result["ips"] == ["192.0.2.20"]


def test_resolve_url_rejects_unsupported_scheme():
    result = resolve_url("ftp://example.com/file")

    assert result["status"] == "invalid"
    assert result["ips"] == []


def test_resolve_url_handles_dns_failure(monkeypatch):
    def fake_getaddrinfo(host, port, type):
        raise socket.gaierror("Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    result = resolve_url("https://unknown.example")

    assert result["host"] == "unknown.example"
    assert result["ips"] == []
    assert result["status"] == "unresolved"


def test_lookup_target_resolves_url(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.30", 0))
        ],
    )

    result = lookup_target("https://api.example.com")

    assert result["host"] == "api.example.com"
    assert result["ips"] == ["192.0.2.30"]
    assert result["type"] == "API"
    assert result["status"] == "resolved"


def test_lookup_target_reverse_resolves_ip(monkeypatch):
    monkeypatch.setattr(
        socket,
        "gethostbyaddr",
        lambda ip: ("dns.google", [], [ip]),
    )

    result = lookup_target("8.8.8.8")

    assert result["host"] == "dns.google"
    assert result["ips"] == ["8.8.8.8"]
    assert result["type"] == "Website"
    assert result["status"] == "resolved"
