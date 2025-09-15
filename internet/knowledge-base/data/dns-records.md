# DNS Records Reference Guide

## Core DNS Record Types

### Address Records

| Record | Purpose | Example | TTL | Description |
|--------|---------|---------|-----|-------------|
| **A** | IPv4 Address | `192.0.2.1` | 5min-24hr | Maps domain name to IPv4 address |
| **AAAA** | IPv6 Address | `2001:db8::1` | 5min-24hr | Maps domain name to IPv6 address |
| **CNAME** | Canonical Name | `www.example.com` | 5min-24hr | Alias pointing to another domain |
| **ALIAS** | Zone Apex Alias | `target.example.com` | 5min | Like CNAME but works at zone apex |

### Mail Records

| Record | Purpose | Example | Priority | TTL |
|--------|---------|---------|----------|-----|
| **MX** | Mail Exchanger | `10 mail.example.com` | Yes (lower = higher priority) | 1-24hr |
| **SPF** | Sender Policy Framework | `v=spf1 ip4:192.0.2.0/24 -all` | No | 1hr |
| **DKIM** | DomainKeys Identified Mail | `v=DKIM1; k=rsa; p=[public_key]` | No | 1hr |
| **DMARC** | Email Authentication Policy | `v=DMARC1; p=reject; rua=mailto:dmarc@example.com` | No | 1hr |

### Infrastructure Records

| Record | Purpose | Example | TTL | Use Case |
|--------|---------|---------|-----|----------|
| **NS** | Name Server | `ns1.example.com` | 24-48hr | Delegates subdomain to nameservers |
| **SOA** | Start of Authority | `ns1.example.com admin.example.com 2024010101 3600 1800 604800 86400` | 24hr | Zone authority information |
| **PTR** | Pointer Record | `host.example.com` | 24hr | Reverse DNS (IP to hostname) |

### Service Records

| Record | Purpose | Format | Priority | Example |
|--------|---------|--------|----------|---------|
| **SRV** | Service Location | `priority weight port target` | Yes | `10 60 5060 sipserver.example.com` |
| **NAPTR** | Naming Authority Pointer | Complex format | Yes | Used for ENUM and service discovery |
| **HTTPS** | HTTPS Service Binding | `priority target parameters` | Yes | `1 . alpn=h3 ipv4hint=192.0.2.1` |
| **SVCB** | Service Binding | `priority target parameters` | Yes | `1 backend.example.com port=8080` |

## Security Records

### DNSSEC Records

| Record | Purpose | Description | Signed |
|--------|---------|-------------|--------|
| **DNSKEY** | DNS Public Key | Contains public key for DNSSEC | No |
| **DS** | Delegation Signer | Links to DNSKEY in child zone | No |
| **RRSIG** | Resource Record Signature | DNSSEC signature for record set | No |
| **NSEC** | Next Secure Record | Proves non-existence in DNSSEC | No |
| **NSEC3** | Next Secure v3 | NSEC with hashed names for privacy | No |

### Certificate Records

| Record | Purpose | Example Use | TTL |
|--------|---------|-------------|-----|
| **CAA** | Certificate Authority Authorization | `0 issue letsencrypt.org` | 1hr |
| **TLSA** | TLS Authentication | DANE certificate pinning | 1hr |
| **CERT** | Certificate Storage | Stores certificates in DNS | 1hr |
| **SSHFP** | SSH Fingerprint | SSH host key verification | 1hr |
| **SMIMEA** | S/MIME Certificate | S/MIME certificate association | 1hr |

## Informational Records

| Record | Purpose | Example | Common Use |
|--------|---------|---------|------------|
| **TXT** | Text Data | Any text string | SPF, DKIM, domain verification |
| **HINFO** | Host Information | `CPU=x86-64 OS=Linux` | Rarely used (security risk) |
| **RP** | Responsible Person | `admin.example.com` | Contact information |
| **LOC** | Location | `51 30 0.000 N 0 7 0.000 W` | Geographic coordinates |

## Special Purpose Records

| Record | Purpose | Use Case |
|--------|---------|----------|
| **APL** | Address Prefix List | Address range lists |
| **DHCID** | DHCP Identifier | Links DHCP clients to DNS |
| **IPSECKEY** | IPsec Key | IPsec public keys |
| **OPENPGPKEY** | OpenPGP Key | OpenPGP public keys |

## Common DNS Configurations

### Basic Website Setup
```dns
example.com.        A       192.0.2.1
example.com.        AAAA    2001:db8::1
www.example.com.    CNAME   example.com.
```

### Email Configuration
```dns
example.com.        MX      10 mail.example.com.
example.com.        MX      20 mail2.example.com.
example.com.        TXT     "v=spf1 mx -all"
_dmarc.example.com. TXT     "v=DMARC1; p=quarantine"
```

### Service Discovery
```dns
_sip._tcp.example.com.     SRV     10 60 5060 sipserver.example.com.
_xmpp-client._tcp.example.com. SRV 5 0 5222 xmpp.example.com.
```

## TTL Guidelines

| Record Type | Recommended TTL | Reason |
|-------------|-----------------|--------|
| NS | 24-48 hours | Rarely changes |
| MX | 1-24 hours | Email continuity |
| A/AAAA | 5 min - 1 hour | Balance between caching and flexibility |
| CNAME | 1 hour | Follows target record |
| TXT (SPF/DKIM) | 1 hour | May need quick updates |
| SOA | 24 hours | Zone configuration |

## DNS Query Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Recursive** | Full resolution from root | End-user queries |
| **Iterative** | Step-by-step resolution | Between DNS servers |
| **Forward** | Domain to IP | Normal lookups |
| **Reverse** | IP to domain | PTR records |

## DNS Response Codes

| Code | Name | Meaning |
|------|------|---------|
| NOERROR | Success | Query completed successfully |
| NXDOMAIN | Non-existent domain | Domain does not exist |
| SERVFAIL | Server failure | DNS server problem |
| REFUSED | Query refused | Server refuses to answer |
| NOTIMP | Not implemented | Unsupported query type |

## Best Practices

### Security
- Enable DNSSEC for domain validation
- Use CAA records to control certificate issuance
- Implement SPF, DKIM, and DMARC for email
- Keep TTLs reasonable to allow quick changes
- Monitor for DNS hijacking

### Performance
- Use appropriate TTL values
- Implement GeoDNS for global services
- Consider anycast for DNS servers
- Monitor query response times
- Use DNS prefetching for web performance

### Reliability
- Multiple NS records (minimum 2)
- Geographically distributed nameservers
- Secondary DNS providers
- Regular DNS health checks
- Proper SOA serial number updates