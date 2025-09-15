# Network Layers Reference Guide

## OSI Model (7 Layers)

### Layer 7: Application Layer
**Function**: User applications and services  
**PDU**: Data  
**Addressing**: Application-specific (URLs, email addresses)

| Protocol | Port | Purpose | Example |
|----------|------|---------|---------|
| HTTP/HTTPS | 80/443 | Web browsing | Chrome, Firefox |
| FTP | 20/21 | File transfer | FileZilla |
| SSH | 22 | Secure shell | PuTTY, OpenSSH |
| DNS | 53 | Name resolution | DNS servers |
| SMTP | 25 | Email sending | Mail servers |
| POP3/IMAP | 110/143 | Email retrieval | Outlook, Gmail |

### Layer 6: Presentation Layer
**Function**: Data translation, encryption, compression  
**PDU**: Data  
**Addressing**: None

| Function | Protocols/Formats | Purpose |
|----------|------------------|---------|
| Encryption | SSL/TLS | Secure communication |
| Compression | JPEG, GIF, ZIP | Reduce data size |
| Translation | ASCII, EBCDIC | Character encoding |
| Serialization | JSON, XML | Data formatting |

### Layer 5: Session Layer
**Function**: Session establishment and management  
**PDU**: Data  
**Addressing**: Session IDs

| Protocol | Purpose | Example |
|----------|---------|---------|
| NetBIOS | Windows networking | File sharing |
| SQL | Database sessions | Database connections |
| RPC | Remote procedure calls | Distributed computing |
| NFS | Network file system | Remote file access |

### Layer 4: Transport Layer
**Function**: End-to-end communication and reliability  
**PDU**: Segment (TCP) / Datagram (UDP)  
**Addressing**: Port numbers (0-65535)  
**Header Size**: TCP: 20-60 bytes, UDP: 8 bytes

| Protocol | Reliability | Ordering | Flow Control | Use Cases |
|----------|------------|----------|--------------|-----------|
| TCP | Yes | Yes | Yes | Web, Email, File transfer |
| UDP | No | No | No | DNS, VoIP, Gaming |
| QUIC | Yes | Yes | Yes | HTTP/3, Modern web |
| SCTP | Optional | Yes | Yes | Telephony signaling |

### Layer 3: Network Layer
**Function**: Routing between networks  
**PDU**: Packet  
**Addressing**: IP addresses  
**Header Size**: IPv4: 20-60 bytes, IPv6: 40 bytes

| Protocol | Version | Address Size | Address Space |
|----------|---------|--------------|---------------|
| IPv4 | 4 | 32 bits | 4.3 billion |
| IPv6 | 6 | 128 bits | 340 undecillion |
| ICMP | - | - | Control messages |
| IPSec | - | - | Security |

### Layer 2: Data Link Layer
**Function**: Node-to-node delivery within a network  
**PDU**: Frame  
**Addressing**: MAC addresses (48 bits)  
**Header Size**: Ethernet: 14-18 bytes

| Protocol | Medium | Speed | Features |
|----------|--------|-------|----------|
| Ethernet | Wired | 10Mbps - 100Gbps | CSMA/CD, full-duplex |
| Wi-Fi | Wireless | 1Mbps - 10Gbps | CSMA/CA, WPA security |
| PPP | Serial | Variable | Point-to-point links |
| ARP | - | - | IP to MAC resolution |

**Sub-layers**:
- **LLC (Logical Link Control)**: Flow control, error checking
- **MAC (Media Access Control)**: Hardware addressing, media access

### Layer 1: Physical Layer
**Function**: Bit transmission over physical medium  
**PDU**: Bits  
**Addressing**: None  
**Components**: Cables, connectors, repeaters, hubs

| Medium | Type | Distance | Speed |
|--------|------|----------|-------|
| Copper (Cat5e) | Electrical | 100m | 1 Gbps |
| Copper (Cat6a) | Electrical | 100m | 10 Gbps |
| Fiber (Single-mode) | Optical | 40km+ | 100+ Gbps |
| Fiber (Multi-mode) | Optical | 2km | 10-100 Gbps |
| Wireless | Radio | Variable | 1Mbps - 10Gbps |

## TCP/IP Model (4 Layers)

### Comparison with OSI

| TCP/IP Layer | OSI Equivalent | Key Difference |
|--------------|----------------|----------------|
| Application | 5-7 (Session, Presentation, Application) | Combined upper layers |
| Transport | 4 (Transport) | Same functionality |
| Internet | 3 (Network) | Focus on IP |
| Network Access | 1-2 (Physical, Data Link) | Combined lower layers |

### Layer 4: Application
**Combines**: OSI Layers 5-7  
**Protocols**: HTTP, FTP, SSH, DNS, SMTP  
**Direct interface with applications**

### Layer 3: Transport
**Same as**: OSI Layer 4  
**Protocols**: TCP, UDP, QUIC  
**Port-based multiplexing**

### Layer 2: Internet
**Same as**: OSI Layer 3  
**Protocols**: IP, ICMP, ARP  
**Global addressing and routing**

### Layer 1: Network Access
**Combines**: OSI Layers 1-2  
**Protocols**: Ethernet, Wi-Fi, PPP  
**Physical transmission and local delivery**

## Protocol Data Units (PDUs)

| Layer | OSI PDU | Contains | Added Information |
|-------|---------|----------|-------------------|
| Application | Data | User data | Application headers |
| Transport | Segment/Datagram | Data + App headers | Port numbers, sequence |
| Network | Packet | Segment + Transport header | IP addresses, TTL |
| Data Link | Frame | Packet + Network header | MAC addresses, CRC |
| Physical | Bits | Frame in binary | Electrical/optical signals |

## Encapsulation Process

```
Application Data
    ↓ [Add Application Header]
Transport Segment (TCP/UDP Header + Data)
    ↓ [Add IP Header]
Network Packet (IP Header + Segment)
    ↓ [Add Frame Header/Trailer]
Data Link Frame (Frame Header + Packet + Frame Trailer)
    ↓ [Convert to Bits]
Physical Bits (Electrical/Optical/Radio Signals)
```

## Addressing at Each Layer

| Layer | Address Type | Format | Example | Scope |
|-------|-------------|--------|---------|-------|
| Application | URL/Email | Variable | www.example.com | Global |
| Transport | Port | 16-bit number | 80, 443, 22 | Host |
| Network | IP | 32/128 bits | 192.168.1.1 | Global |
| Data Link | MAC | 48 bits | AA:BB:CC:DD:EE:FF | Local |
| Physical | None | - | - | - |

## Layer Interactions

### Same-Layer Communication
- **Horizontal**: Protocols at same layer communicate virtually
- **Headers**: Each layer adds its own header information
- **Peer-to-peer**: Logical communication between same layers

### Adjacent-Layer Communication
- **Vertical**: Services provided to layer above
- **SAP**: Service Access Points between layers
- **Primitives**: Request, Indication, Response, Confirmation

## Common Network Devices by Layer

| Layer | Devices | Function |
|-------|---------|----------|
| Application | Proxy, Gateway | Application-level filtering |
| Transport | - | Typically software-based |
| Network | Router, L3 Switch | Routing decisions |
| Data Link | Switch, Bridge | Frame forwarding |
| Physical | Hub, Repeater | Signal amplification |

## Troubleshooting by Layer

### Bottom-Up Approach

1. **Physical**: Check cables, link lights
2. **Data Link**: Verify MAC addresses, VLANs
3. **Network**: Test IP connectivity, routing
4. **Transport**: Check ports, firewall rules
5. **Application**: Verify application configuration

### Layer-Specific Tools

| Layer | Tools | Purpose |
|-------|-------|---------|
| Physical | Cable tester, Light meter | Physical connectivity |
| Data Link | arp, Wireshark | MAC resolution, frame analysis |
| Network | ping, traceroute, ip route | IP connectivity, routing |
| Transport | netstat, ss, telnet | Port status, connections |
| Application | curl, dig, browser tools | Application testing |

## Modern Considerations

### Cross-Layer Optimization
- **TCP/IP**: More practical than strict OSI
- **QUIC**: Combines transport and crypto at L4
- **SDN**: Programmable separation of control/data planes

### Cloud and Virtualization
- **Overlay Networks**: VXLAN, GRE tunneling
- **Container Networking**: Bridge, host, overlay modes
- **Service Mesh**: Application-layer networking

### Security at Each Layer
| Layer | Security Measures |
|-------|------------------|
| Application | WAF, API security |
| Transport | TLS/SSL |
| Network | IPSec, firewall rules |
| Data Link | 802.1X, MAC filtering |
| Physical | Physical security, encryption |