# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities to **<security@sensorapi.dev>** (or create a GitHub Security Advisory).

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

When reporting a vulnerability, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Possible impact
- Any suggested fixes

### Response Timeline

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 2 business days
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will keep you informed of our progress every 7 days until resolution
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### Responsible Disclosure

We ask that you:

- Give us reasonable time to investigate and fix the issue before making it public
- Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of services
- Only interact with accounts you own or with explicit permission of the account holder

### Recognition

We will acknowledge security researchers who responsibly disclose vulnerabilities to us in our release notes and security advisories (unless you prefer to remain anonymous).

## Security Best Practices

### For Developers

- Keep dependencies up to date
- Use environment variables for sensitive configuration
- Never commit secrets to version control
- Implement proper input validation
- Use parameterized queries to prevent SQL injection
- Implement rate limiting and authentication

### For Deployments

- Use HTTPS in production
- Regularly rotate database passwords and API keys
- Monitor for security vulnerabilities in dependencies
- Implement proper logging and monitoring
- Use secure database configurations
- Regularly backup data

## Contact

For security-related questions or concerns, please contact us at <security@sensorapi.dev>
