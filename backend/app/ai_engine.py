from dataclasses import dataclass
import torch
from torch import nn


@dataclass
class AiFinding:
    name: str
    severity: str
    confidence: float
    description: str
    proposal_title: str
    proposal_plan: str


class RiskPrioritizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 3),
            nn.Softmax(dim=0),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features)


class PentestAIAgent:
    def __init__(self):
        torch.manual_seed(7)
        self.model = RiskPrioritizer()

    def _extract_features(self, open_ports: list[int], fingerprint: str) -> torch.Tensor:
        risky_ports = [21, 23, 445, 3389, 6379]
        risk_count = sum(1 for port in open_ports if port in risky_ports)
        has_plaintext = int(any(port in open_ports for port in [21, 23, 110]))
        exposed_db = int(any(port in open_ports for port in [3306, 5432, 6379]))
        web_surface = int(any(port in open_ports for port in [80, 443, 8080]))
        return torch.tensor([
            float(len(open_ports)) / 10.0,
            float(risk_count) / 5.0,
            float(has_plaintext),
            float(exposed_db + web_surface) / 2.0,
        ])

    def analyze(self, open_ports: list[int], fingerprint: str) -> tuple[float, list[AiFinding]]:
        features = self._extract_features(open_ports, fingerprint)
        prediction = self.model(features)
        low, medium, high = prediction.tolist()
        risk_score = min(100.0, (medium * 50.0 + high * 100.0))

        findings: list[AiFinding] = []

        if any(port in open_ports for port in [21, 23]):
            findings.append(
                AiFinding(
                    name="Insecure legacy service exposed",
                    severity="high",
                    confidence=min(0.95, 0.55 + high),
                    description="Detected plaintext protocol (FTP/Telnet), increasing credential theft risk.",
                    proposal_title="Validate service hardening in controlled test",
                    proposal_plan=(
                        "Plan: run authenticated checks in an isolated environment, verify weak auth paths, "
                        "and document remediation. Requires explicit human approval before any intrusive test."
                    ),
                )
            )

        if any(port in open_ports for port in [3306, 5432, 6379]):
            findings.append(
                AiFinding(
                    name="Database service reachable",
                    severity="medium",
                    confidence=min(0.9, 0.5 + medium),
                    description="A database port appears exposed; validate network segmentation and authentication.",
                    proposal_title="Perform authorized configuration review",
                    proposal_plan=(
                        "Plan: with owner approval, validate TLS/auth configuration and least-privilege policies. "
                        "Do not execute exploitation; gather evidence for mitigation only."
                    ),
                )
            )

        if any(port in open_ports for port in [80, 443, 8080]):
            findings.append(
                AiFinding(
                    name="Web attack surface detected",
                    severity="medium",
                    confidence=min(0.88, 0.45 + medium),
                    description="Web service detected; recommended to run authenticated vulnerability checks.",
                    proposal_title="Run approved web security test plan",
                    proposal_plan=(
                        "Plan: execute non-destructive checks first (headers, TLS, outdated frameworks), "
                        "then only proceed with deeper tests after human acceptance."
                    ),
                )
            )

        if not findings:
            findings.append(
                AiFinding(
                    name="Low immediate risk footprint",
                    severity="low",
                    confidence=max(0.4, low),
                    description="No common high-risk exposed services detected in quick scan.",
                    proposal_title="Continue periodic monitoring",
                    proposal_plan="Plan: keep baseline scans and review changes over time.",
                )
            )

        return risk_score, findings
