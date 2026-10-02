# Auth Service Architecture & Runbook

## Overview
The Authentication Service handles user identity, password hashing (Argon2id/bcrypt), JWT token issuance, and OAuth2 SSO handshakes.

## Key Design Characteristics
- Stateless JWT tokens signed with RS256/HS256 algorithms.
- Token expiration: 60 minutes for access tokens, 7 days for refresh tokens.
- Redis-backed rate limiting per IP and client API key.
- Circuit breaker protection for external OAuth identity providers.
