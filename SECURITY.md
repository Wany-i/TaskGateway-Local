# Security Policy

## Supported versions

Security fixes are applied to the latest released minor version. Pre-`1.0` releases may receive breaking security fixes.

## Reporting a vulnerability

Please do not open a public issue for suspected vulnerabilities. Use GitHub's private vulnerability reporting feature for `wany-i/TaskGateway-Local`. Include a minimal reproduction, affected revision, impact, and any suggested mitigation. Do not include credentials, private resource contents, or personal data.

Maintainers aim to acknowledge reports within 7 days and to provide a status update within 14 days. Coordinated disclosure will follow after a fix or mitigation is available.

## Scope

Report issues that could bypass authorization checks, cause the gateway to execute an action, expose indexed data unexpectedly, or introduce dependency/workflow supply-chain risk. The gateway is not a security boundary for resources or hosts that callers have already authorized outside this project.
