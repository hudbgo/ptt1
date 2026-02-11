import socket

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "TELNET",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NETBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MYSQL",
    3389: "RDP",
    5432: "POSTGRES",
    6379: "REDIS",
    8080: "HTTP-ALT",
}


def run_light_scan(target: str, timeout: float = 0.2) -> tuple[list[int], str]:
    open_ports: list[int] = []
    fingerprints: list[str] = []

    for port, service in COMMON_PORTS.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
                fingerprints.append(f"{service}:{port}")
        except OSError:
            continue
        finally:
            sock.close()

    fingerprint = ", ".join(fingerprints) if fingerprints else "No common ports discovered"
    return open_ports, fingerprint
