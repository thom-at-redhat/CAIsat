# Security Policy

<!-- Assisted by: cursor, claude -->

## Supported Versions

| Branch / release | Supported |
| ---------------- | --------- |
| `main`           | Yes       |

Security fixes are applied on the default branch. Deploy from tagged releases or `main` at your own risk for demo workloads.

## Reporting a Vulnerability

**Do not** open a public GitHub issue for security vulnerabilities.

Report issues privately using one of:

1. **GitHub Security Advisories (preferred):** open **Security → Advisories → Report a vulnerability** on this repository.
2. **Email:** Contact the repository maintainers through your organization's standard security channel if you cannot use GitHub advisories.

Include:

- Description of the vulnerability and impact
- Steps to reproduce
- Affected components (Helm chart, backend, frontend, CI)
- Suggested fix or mitigation, if known

We aim to acknowledge reports within **5 business days** and will coordinate disclosure timing with you.

## Scope

This policy covers the CAIsat application source, Helm chart, GitHub Actions workflows, and container build contexts in this repository.

It does **not** cover third-party model endpoints, Quay images you mirror separately, or cluster-level OpenShift/RHOAI configuration outside this repo.

## Upstream

Canonical upstream is [`rh-ai-quickstart/CAIsat`](https://github.com/rh-ai-quickstart/CAIsat).

If your finding applies to upstream and this fork, report to the fork first; we will coordinate upstream disclosure when an upstream PR is opened.
