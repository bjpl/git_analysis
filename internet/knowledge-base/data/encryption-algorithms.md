# Encryption Algorithms Reference

## Symmetric Encryption

### Current Standards

| Algorithm | Key Size | Block Size | Speed | Security | Use Cases |
|-----------|----------|------------|-------|----------|-----------|
| **AES-128** | 128 bits | 128 bits | Very Fast | Good | TLS, disk encryption, VPNs |
| **AES-192** | 192 bits | 128 bits | Very Fast | Excellent | High security applications |
| **AES-256** | 256 bits | 128 bits | Very Fast | Excellent | Top secret, long-term security |
| **ChaCha20** | 256 bits | 512 bits | Fast | Excellent | Mobile, TLS 1.3, WireGuard |

### Legacy Algorithms (Avoid)

| Algorithm | Status | Issue | Migration Path |
|-----------|--------|-------|----------------|
| **3DES** | Deprecated | 64-bit block size, slow | → AES |
| **Blowfish** | Obsolete | 64-bit block size | → AES or ChaCha20 |
| **RC4** | Broken | Stream cipher biases | → AES-GCM or ChaCha20 |
| **DES** | Broken | 56-bit key too small | → AES |

## Asymmetric Encryption

### RSA Key Sizes

| Key Size | Security Level | Performance | Recommendation |
|----------|---------------|-------------|----------------|
| **1024 bits** | Broken | Fast | Never use |
| **2048 bits** | Good | Moderate | Current minimum |
| **3072 bits** | Better | Slower | Recommended |
| **4096 bits** | Excellent | Very Slow | High security only |

### Elliptic Curve Cryptography

| Curve | Key Size | Security Equivalent | Use Cases |
|-------|----------|-------------------|-----------|
| **P-256** | 256 bits | RSA-3072 | TLS, mobile devices |
| **P-384** | 384 bits | RSA-7680 | High security |
| **P-521** | 521 bits | RSA-15360 | Maximum security |
| **Curve25519** | 256 bits | RSA-3072 | Modern crypto, WireGuard |
| **Ed25519** | 256 bits | RSA-3072 | SSH keys, signatures |

## Hash Functions

### Secure Hash Algorithms

| Algorithm | Output Size | Speed | Status | Use Cases |
|-----------|------------|-------|--------|-----------|
| **SHA-256** | 256 bits | Fast | Secure | Certificates, Bitcoin, general |
| **SHA-384** | 384 bits | Fast | Secure | High security |
| **SHA-512** | 512 bits | Fast | Secure | 64-bit optimized |
| **SHA3-256** | 256 bits | Moderate | Secure | Future-proofing |
| **SHA3-512** | 512 bits | Moderate | Secure | Maximum security |
| **BLAKE2b** | 1-512 bits | Very Fast | Secure | Checksums, hashing |
| **BLAKE3** | 256 bits | Extremely Fast | Secure | High performance |

### Broken Hash Functions

| Algorithm | Status | Vulnerability | Alternative |
|-----------|--------|--------------|-------------|
| **MD5** | Broken | Collisions trivial | SHA-256 |
| **SHA-1** | Broken | Collisions demonstrated | SHA-256 |

## Password Hashing (KDF)

### Recommended Algorithms

| Algorithm | Memory Hard | Parallelism | Recommendation |
|-----------|------------|-------------|----------------|
| **Argon2id** | Yes | Configurable | Best choice for new systems |
| **scrypt** | Yes | Limited | Good for cryptocurrencies |
| **bcrypt** | No | No | Good for web applications |
| **PBKDF2** | No | No | Minimum acceptable |

### Configuration Guidelines

```
Argon2id: memory=64MB, iterations=3, parallelism=4
scrypt:   N=2^14, r=8, p=1
bcrypt:   cost factor=12 minimum
PBKDF2:   100,000+ iterations minimum
```

## Digital Signatures

| Algorithm | Key Type | Security | Speed | Use Cases |
|-----------|----------|----------|-------|-----------|
| **EdDSA** | Ed25519 | Excellent | Very Fast | Modern protocols |
| **ECDSA** | ECC | Good | Fast | TLS, cryptocurrencies |
| **RSA-PSS** | RSA | Good | Slow | Certificates |
| **DSA** | DSA | Weak | Slow | Legacy only |

## Message Authentication Codes (MAC)

| Algorithm | Based On | Output Size | Use Cases |
|-----------|----------|-------------|-----------|
| **HMAC-SHA256** | SHA-256 | 256 bits | API authentication |
| **HMAC-SHA512** | SHA-512 | 512 bits | High security |
| **Poly1305** | ChaCha20 | 128 bits | AEAD constructions |
| **GMAC** | AES-GCM | 128 bits | AES-GCM authentication |

## Authenticated Encryption (AEAD)

| Algorithm | Encryption | Authentication | Use Cases |
|-----------|------------|----------------|-----------|
| **AES-GCM** | AES | GMAC | TLS 1.2+, IPSec |
| **ChaCha20-Poly1305** | ChaCha20 | Poly1305 | TLS 1.3, WireGuard |
| **AES-CCM** | AES | CBC-MAC | IoT devices |
| **XChaCha20-Poly1305** | XChaCha20 | Poly1305 | File encryption |

## Quantum Resistance

### Current Status

| Category | Quantum Vulnerable | Post-Quantum Alternatives |
|----------|-------------------|--------------------------|
| **Symmetric** | Weakened (halved strength) | Double key sizes |
| **RSA/ECC** | Completely broken | Lattice, code, hash-based |
| **Hash** | Weakened (2/3 strength) | Increase output size |

### NIST Post-Quantum Finalists

| Algorithm | Type | Use Case | Status |
|-----------|------|----------|--------|
| **CRYSTALS-Kyber** | KEM | Key exchange | Selected |
| **CRYSTALS-Dilithium** | Signature | Digital signatures | Selected |
| **FALCON** | Signature | Constrained devices | Selected |
| **SPHINCS+** | Signature | Stateless hash-based | Selected |

## Performance Comparison

### Encryption Speed (MB/s on modern CPU)

```
AES-128-GCM:        3000+ MB/s (with AES-NI)
ChaCha20-Poly1305:  2000+ MB/s
AES-256-GCM:        2500+ MB/s (with AES-NI)
AES-128-CBC:        1500+ MB/s
3DES:               50-100 MB/s
```

### Signature Generation (ops/sec)

```
Ed25519:      50,000+ ops/sec
ECDSA-P256:   20,000+ ops/sec
RSA-2048:     1,000+ ops/sec
RSA-4096:     100+ ops/sec
```

## Security Recommendations

### Minimum Key Sizes (2024)

| Algorithm | Minimum | Recommended |
|-----------|---------|-------------|
| **Symmetric** | 128 bits | 256 bits |
| **RSA** | 2048 bits | 3072 bits |
| **ECC** | 256 bits | 384 bits |
| **Hash** | 256 bits | 256 bits |

### Protocol Recommendations

| Protocol | Algorithms | Configuration |
|----------|------------|---------------|
| **TLS 1.3** | AES-GCM, ChaCha20-Poly1305 | ECDHE only |
| **SSH** | Ed25519, AES-GCM | Disable weak algorithms |
| **VPN** | AES-256-GCM, ChaCha20-Poly1305 | Perfect forward secrecy |
| **Disk Encryption** | AES-256-XTS | Hardware acceleration |

## Migration Guidelines

### From Legacy to Modern

| From | To | Reason |
|------|-----|--------|
| 3DES → | AES-256 | Block size, speed |
| SHA-1 → | SHA-256 | Collision resistance |
| RSA-1024 → | RSA-3072 or ECC-P256 | Key strength |
| PBKDF2 → | Argon2id | Memory hardness |
| CBC mode → | GCM or ChaCha20-Poly1305 | AEAD |