"""Controlled execution engine for safe, pre-approved checks.

This module is intentionally separated from AI analysis:
- AI suggests actions only.
- Execution engine runs only allowlisted, read-only checks.
- Human approval is mandatory before any run.
"""

from __future__ import annotations

from datetime import datetime
import json
import logging
import socket
import urllib.request
from urllib.parse import urlparse


logger = logging.getLogger("execution_engine")
if not logger.handlers:
    file_handler = logging.FileHandler("execution_engine.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class ExecutionError(Exception):
    pass


ALLOWED_ACTIONS = {
    "dns_resolve",
    "tcp_connectivity_check",
    "http_head_check",
}


def validate_action(action_key: str, params: dict) -> None:
    if action_key not in ALLOWED_ACTIONS:
        raise ExecutionError(f"Action '{action_key}' is not allowlisted")

    if action_key == "dns_resolve":
        if params:
            raise ExecutionError("dns_resolve does not accept parameters")

    if action_key == "tcp_connectivity_check":
        ports = params.get("ports")
        timeout = params.get("timeout", 1.0)
        if not isinstance(ports, list) or not ports:
            raise ExecutionError("tcp_connectivity_check requires non-empty ports list")
        if any((not isinstance(p, int) or p < 1 or p > 65535) for p in ports):
            raise ExecutionError("ports must contain valid TCP ports")
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 10:
            raise ExecutionError("timeout must be between 0 and 10 seconds")

    if action_key == "http_head_check":
        path = params.get("path", "/")
        if not isinstance(path, str) or not path.startswith("/"):
            raise ExecutionError("path must be a string starting with '/'")


def execute_action(action_key: str, target: str, params: dict) -> dict:
    """Execute a single safe action with structured results and full logging."""
    validate_action(action_key, params)

    started_at = datetime.utcnow().isoformat()
    logger.info("execute_start action=%s target=%s params=%s", action_key, target, json.dumps(params))

    try:
        if action_key == "dns_resolve":
            ip = socket.gethostbyname(target)
            result = {"resolved_ip": ip}

        elif action_key == "tcp_connectivity_check":
            timeout = float(params.get("timeout", 1.0))
            checks = []
            for port in params["ports"]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                try:
                    code = sock.connect_ex((target, port))
                    checks.append({"port": port, "open": code == 0})
                finally:
                    sock.close()
            result = {"checks": checks}

        elif action_key == "http_head_check":
            path = params.get("path", "/")
            parsed = urlparse(target if target.startswith("http") else f"http://{target}")
            url = f"{parsed.scheme}://{parsed.netloc}{path}"
            req = urllib.request.Request(url=url, method="HEAD")
            with urllib.request.urlopen(req, timeout=4) as resp:
                result = {"url": url, "status_code": resp.status, "headers": dict(resp.headers.items())}
        else:
            raise ExecutionError("Unknown action")

        logger.info("execute_success action=%s target=%s", action_key, target)
        return {
            "status": "success",
            "action_key": action_key,
            "target": target,
            "result": result,
            "started_at": started_at,
            "finished_at": datetime.utcnow().isoformat(),
        }
    except Exception as exc:  # controlled boundary for standardized result format
        logger.exception("execute_error action=%s target=%s error=%s", action_key, target, str(exc))
        return {
            "status": "error",
            "action_key": action_key,
            "target": target,
            "error": str(exc),
            "started_at": started_at,
            "finished_at": datetime.utcnow().isoformat(),
        }
