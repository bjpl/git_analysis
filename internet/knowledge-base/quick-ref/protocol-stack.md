# Protocol Stack Quick Reference

## TCP/IP Model vs OSI Model

| TCP/IP Layer | OSI Layers | Protocols | Function |
|--------------|------------|-----------|----------|
| Application | 5-7: Application, Presentation, Session | HTTP, HTTPS, FTP, SSH, DNS, SMTP | User applications and services |
| Transport | 4: Transport | TCP, UDP, QUIC, SCTP | End-to-end communication, reliability |
| Internet | 3: Network | IPv4, IPv6, ICMP, IPSec | Routing between networks |
| Link | 1-2: Physical, Data Link | Ethernet, Wi-Fi, PPP, ARP | Local network communication |

## Common Protocol Details

### Application Layer Protocols

| Protocol | Port | Transport | Purpose | Key Features |
|----------|------|-----------|---------|--------------|
| HTTP | 80 | TCP | Web browsing | Stateless, request-response |
| HTTPS | 443 | TCP | Secure web | HTTP + TLS encryption |
| HTTP/3 | 443 | QUIC/UDP | Modern web | Multiplexing, 0-RTT |
| DNS | 53 | UDP/TCP | Name resolution | Hierarchical, cached |
| SSH | 22 | TCP | Secure shell | Encrypted remote access |
| FTP | 20/21 | TCP | File transfer | Separate control/data |
| SMTP | 25 | TCP | Email sending | Store and forward |
| POP3 | 110 | TCP | Email retrieval | Download and delete |
| IMAP | 143 | TCP | Email access | Server-side storage |
| NTP | 123 | UDP | Time sync | Stratum hierarchy |
| DHCP | 67/68 | UDP | IP configuration | Automatic network config |
| SNMP | 161 | UDP | Network management | Monitoring and control |

### Transport Layer Protocols

| Protocol | Reliability | Ordering | Flow Control | Use Cases |
|----------|------------|----------|--------------|-----------|
| TCP | Yes | Yes | Yes | Web, email, file transfer |
| UDP | No | No | No | DNS, VoIP, gaming |
| QUIC | Yes | Yes | Yes | HTTP/3, modern apps |
| SCTP | Optional | Yes | Yes | Telephony signaling |

### Network Layer Protocols

| Protocol | Version | Address Size | Address Space | Header Size |
|----------|---------|--------------|---------------|-------------|
| IPv4 | 4 | 32 bits | 4.3 billion | 20-60 bytes |
| IPv6 | 6 | 128 bits | 340 undecillion | 40 bytes fixed |
| ICMP | - | - | - | 8+ bytes |
| IPSec | - | - | - | Variable |

## Protocol Encapsulation

```
Application Data
    ↓ [Add Application Header]
Transport Segment (TCP/UDP Header + Data)
    ↓ [Add IP Header]
Network Packet (IP Header + Segment)
    ↓ [Add Frame Header/Trailer]
Link Frame (Frame Header + Packet + Trailer)
    ↓ [Convert to Bits]
Physical Bits (Electrical/Optical Signals)
```

## MTU Sizes

| Network Type | MTU (bytes) | Notes |
|--------------|-------------|-------|
| Ethernet | 1500 | Standard LAN |
| Jumbo Frames | 9000 | Data center |
| Wi-Fi | 2304 | 802.11 |
| PPPoE | 1492 | DSL common |
| IPv6 Minimum | 1280 | Required minimum |
| IPv4 Minimum | 68 | Theoretical minimum |

## Common Port Ranges

| Range | Type | Usage |
|-------|------|-------|
| 0-1023 | Well-known | System services |
| 1024-49151 | Registered | User applications |
| 49152-65535 | Dynamic/Private | Ephemeral ports |

## TCP Flags

| Flag | Name | Purpose |
|------|------|---------|
| SYN | Synchronize | Initiate connection |
| ACK | Acknowledge | Acknowledge receipt |
| FIN | Finish | Close connection |
| RST | Reset | Abort connection |
| PSH | Push | Send immediately |
| URG | Urgent | Priority data |

## ICMP Types (Common)

| Type | Name | Purpose |
|------|------|---------|
| 0 | Echo Reply | Ping response |
| 3 | Destination Unreachable | Various error codes |
| 5 | Redirect | Better route available |
| 8 | Echo Request | Ping request |
| 11 | Time Exceeded | TTL expired |

## HTTP Methods

| Method | Idempotent | Safe | Purpose |
|--------|------------|------|---------|
| GET | Yes | Yes | Retrieve resource |
| POST | No | No | Submit data |
| PUT | Yes | No | Replace resource |
| DELETE | Yes | No | Remove resource |
| HEAD | Yes | Yes | Get headers only |
| OPTIONS | Yes | Yes | Get allowed methods |
| PATCH | No | No | Partial update |

## DNS Record Types

| Type | Purpose | Example |
|------|---------|---------|
| A | IPv4 address | 192.0.2.1 |
| AAAA | IPv6 address | 2001:db8::1 |
| CNAME | Canonical name | www → example.com |
| MX | Mail server | 10 mail.example.com |
| NS | Name server | ns1.example.com |
| TXT | Text data | SPF, DKIM records |
| SOA | Start of authority | Zone information |
| PTR | Reverse lookup | IP to hostname |
| SRV | Service location | _sip._tcp.example.com |