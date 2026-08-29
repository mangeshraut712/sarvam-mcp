# Security Policy

## Supported versions

Please report issues against the default branch of this repository (`main`).

## Reporting a vulnerability

**Do not** open a public GitHub issue for security problems.

Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-vulnerability) on this repository, or email the maintainer listed on the GitHub profile.

Include:

- Affected component (`sarvam-mcp` server vs `web/` Vaani)
- Impact (auth bypass, key leak, SSRF, etc.)
- Reproduction only as far as needed to confirm — no exploit kits

We will acknowledge reports as soon as we can and work on a fix before any public disclosure.

## API keys

Never commit `SARVAM_API_KEY`, `~/.sarvam/credentials`, or `.env` files. Rotate a key immediately if it may have leaked.
