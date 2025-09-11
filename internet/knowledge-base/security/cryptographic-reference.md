# Cryptographic Reference Guide

## Encryption Algorithm Comparison

### Symmetric Encryption

| Algorithm | Key Size | Block Size | Speed | Security | Use Cases |
|-----------|----------|------------|-------|----------|-----------|
| AES | 128/192/256 bits | 128 bits | Very Fast* | Excellent | TLS, disk encryption, VPNs |
| ChaCha20 | 256 bits | 512 bits | Fast | Excellent | Mobile, TLS 1.3, WireGuard |
| 3DES | 168 bits | 64 bits | Slow | Weak | Legacy systems only |
| Blowfish | 32-448 bits | 64 bits | Fast | Moderate | Legacy, replaced by Twofish |
| Twofish | 128/192/256 bits | 128 bits | Fast | Good | Disk encryption alternative |

*With hardware acceleration (AES-NI)

### Asymmetric Encryption

| Algorithm | Key Size | Security Level | Performance | Quantum Resistant |
|-----------|----------|----------------|-------------|-------------------|
| RSA-2048 | 2048 bits | 112 bits | Slow | No |
| RSA-4096 | 4096 bits | 128 bits | Very Slow | No |
| ECC P-256 | 256 bits | 128 bits | Fast | No |
| ECC P-384 | 384 bits | 192 bits | Moderate | No |
| Ed25519 | 256 bits | 128 bits | Very Fast | No |

### Hash Functions

| Algorithm | Output Size | Speed | Status | Collision Resistance |
|-----------|-------------|-------|---------|---------------------|
| MD5 | 128 bits | Very Fast | Broken | No (collisions found) |
| SHA-1 | 160 bits | Fast | Deprecated | No (collisions found) |
| SHA-256 | 256 bits | Fast | Secure | Yes |
| SHA-512 | 512 bits | Fast* | Secure | Yes |
| SHA-3-256 | 256 bits | Moderate | Secure | Yes |
| BLAKE2b | 1-512 bits | Very Fast | Secure | Yes |
| BLAKE3 | 256 bits | Extremely Fast | Secure | Yes |

*Faster than SHA-256 on 64-bit systems

## TLS Cipher Suite Recommendations

### TLS 1.3 Cipher Suites (Recommended)
```
TLS_AES_256_GCM_SHA384
TLS_AES_128_GCM_SHA256
TLS_CHACHA20_POLY1305_SHA256
```

### TLS 1.2 Strong Cipher Suites
```
# ECDHE with AES-GCM (Recommended)
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

# ECDHE with ChaCha20 (Good for mobile)
TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
```

### Weak/Deprecated Cipher Suites (Avoid)
```
# No forward secrecy
TLS_RSA_WITH_*

# Weak encryption
*_WITH_RC4_*
*_WITH_DES_*
*_WITH_3DES_*

# Weak hashing
*_MD5
*_SHA1

# No authentication
*_WITH_NULL_*
*_anon_*
```

## Key Derivation Functions (KDF)

| Function | Purpose | Iterations | Salt Required | Use Cases |
|----------|---------|------------|---------------|-----------|
| PBKDF2 | Password hashing | 100,000+ | Yes | Legacy, widely supported |
| bcrypt | Password hashing | Cost 12+ | Built-in | Web applications |
| scrypt | Password hashing | N=16384 | Yes | Cryptocurrency wallets |
| Argon2id | Password hashing | Memory-hard | Yes | Modern best practice |
| HKDF | Key derivation | N/A | Optional | TLS, protocol keys |

## Digital Signature Algorithms

| Algorithm | Signature Size | Speed | Security | Use Cases |
|-----------|----------------|-------|----------|-----------|
| RSA-PSS | Key size | Slow | Good | Certificates, general |
| ECDSA | 2 × curve size | Fast | Good | TLS, Bitcoin |
| EdDSA (Ed25519) | 512 bits | Very Fast | Excellent | SSH, modern protocols |
| DSA | 448 bits | Slow | Weak | Legacy only |

## Certificate Key Requirements

### Current Recommendations (2024)
- **RSA**: Minimum 2048 bits, recommend 3072 bits
- **ECC**: Minimum P-256, recommend P-384
- **Validity**: Maximum 397 days (13 months)
- **Hash**: SHA-256 minimum

### Future Requirements (2030+)
- **RSA**: Minimum 3072 bits, recommend 4096 bits
- **ECC**: Minimum P-384, consider post-quantum
- **Hash**: SHA-384 or SHA-3

## VPN Protocol Security Comparison

| Protocol | Encryption | Authentication | Forward Secrecy | Performance |
|----------|------------|----------------|-----------------|-------------|
| OpenVPN | AES-256-GCM | Certificates/PSK | Yes (DHE/ECDHE) | Moderate |
| WireGuard | ChaCha20 | Curve25519 | Yes | Excellent |
| IPSec/IKEv2 | AES-256 | Certificates/PSK | Yes | Good |
| L2TP/IPSec | AES-256 | PSK | Optional | Moderate |
| PPTP | MPPE (RC4) | MS-CHAPv2 | No | Fast but insecure |

## Security Protocol Ports

| Protocol | Port | Transport | Encrypted |
|----------|------|-----------|-----------|
| HTTPS | 443 | TCP | Yes |
| SSH | 22 | TCP | Yes |
| SFTP | 22 | TCP | Yes (over SSH) |
| FTPS | 990 | TCP | Yes |
| SMTPS | 465 | TCP | Yes |
| IMAPS | 993 | TCP | Yes |
| POP3S | 995 | TCP | Yes |
| OpenVPN | 1194 | UDP/TCP | Yes |
| WireGuard | 51820 | UDP | Yes |
| IPSec | 500/4500 | UDP | Yes |

## Certificate Validation Checks

### Standard X.509 Validation
1. **Signature verification** - Cryptographic validity
2. **Certificate chain** - Links to trusted root
3. **Validity period** - Not expired or future-dated
4. **Key usage** - Appropriate for purpose
5. **Name matching** - Subject matches expected
6. **Revocation status** - CRL or OCSP check

### Additional Security Checks
- **CT logs** - Certificate Transparency
- **CAA records** - DNS authorization
- **Pin validation** - HPKP (deprecated) or static pins
- **DANE/TLSA** - DNS-based authentication

## Common Cryptographic Attacks

| Attack Type | Target | Mitigation |
|-------------|--------|------------|
| Brute Force | Weak keys | Longer keys, rate limiting |
| Dictionary | Passwords | Salting, slow hashing |
| Rainbow Tables | Hashed passwords | Salting |
| Timing Attack | Crypto operations | Constant-time algorithms |
| Padding Oracle | Block ciphers | AEAD modes (GCM) |
| Birthday Attack | Hash collisions | Larger hash output |
| BEAST | TLS 1.0 CBC | Use TLS 1.2+ |
| CRIME/BREACH | Compression | Disable compression |
| POODLE | SSLv3 | Disable SSLv3 |
| Heartbleed | OpenSSL | Patch, perfect forward secrecy |