# Security Policy

## Supported version
Security fixes target the latest release on `main`.

## Reporting
Please use GitHub's private vulnerability reporting feature when available. Do not publish credentials, private URLs, database contents, or personal data in a public issue.

## Security model
Shortlink Analytics validates destination schemes, rejects embedded URL credentials, parameterizes SQLite queries, and intentionally does not store visitor IP addresses, cookies, full referrer URLs, or browser fingerprints. The built-in Flask server is intended for local/development use; deploy behind a production WSGI server and HTTPS reverse proxy for public traffic.
