# Common Network Ports Quick Reference

## Well-Known Ports (0-1023)

### Essential Services
| Port | Protocol | Service | Description | Encrypted |
|------|----------|---------|-------------|-----------|
| 20 | TCP | FTP-DATA | File Transfer Protocol (Data) | No |
| 21 | TCP | FTP | File Transfer Protocol (Control) | No |
| 22 | TCP | SSH | Secure Shell | Yes |
| 23 | TCP | Telnet | Unencrypted remote access | No |
| 25 | TCP | SMTP | Simple Mail Transfer Protocol | No* |
| 53 | TCP/UDP | DNS | Domain Name System | No* |
| 67 | UDP | DHCP | Dynamic Host Configuration (Server) | No |
| 68 | UDP | DHCP | Dynamic Host Configuration (Client) | No |
| 69 | UDP | TFTP | Trivial File Transfer Protocol | No |
| 80 | TCP | HTTP | Hypertext Transfer Protocol | No |
| 110 | TCP | POP3 | Post Office Protocol v3 | No* |
| 119 | TCP | NNTP | Network News Transfer Protocol | No |
| 123 | UDP | NTP | Network Time Protocol | No |
| 135 | TCP | RPC | Microsoft RPC | No |
| 137 | UDP | NetBIOS | NetBIOS Name Service | No |
| 138 | UDP | NetBIOS | NetBIOS Datagram | No |
| 139 | TCP | NetBIOS | NetBIOS Session | No |
| 143 | TCP | IMAP | Internet Message Access Protocol | No* |
| 161 | UDP | SNMP | Simple Network Management Protocol | No |
| 162 | UDP | SNMPTRAP | SNMP Trap | No |
| 179 | TCP | BGP | Border Gateway Protocol | No* |
| 389 | TCP | LDAP | Lightweight Directory Access Protocol | No |
| 443 | TCP | HTTPS | HTTP Secure | Yes |
| 445 | TCP | SMB | Server Message Block | No* |
| 465 | TCP | SMTPS | SMTP Secure (deprecated) | Yes |
| 500 | UDP | IKE | Internet Key Exchange (IPSec) | Yes |
| 514 | UDP | Syslog | System Logging | No |
| 515 | TCP | LPD | Line Printer Daemon | No |
| 520 | UDP | RIP | Routing Information Protocol | No |
| 587 | TCP | SMTP | Mail Submission | No* |
| 636 | TCP | LDAPS | LDAP Secure | Yes |
| 853 | TCP | DoT | DNS over TLS | Yes |
| 989 | TCP | FTPS | FTP Secure (Data) | Yes |
| 990 | TCP | FTPS | FTP Secure (Control) | Yes |
| 993 | TCP | IMAPS | IMAP Secure | Yes |
| 995 | TCP | POP3S | POP3 Secure | Yes |

*Can use STARTTLS for encryption

## Registered Ports (1024-49151)

### Database Services
| Port | Service | Description |
|------|---------|-------------|
| 1433 | MS SQL | Microsoft SQL Server |
| 1521 | Oracle | Oracle Database |
| 3306 | MySQL | MySQL Database |
| 5432 | PostgreSQL | PostgreSQL Database |
| 5984 | CouchDB | Apache CouchDB |
| 6379 | Redis | Redis Database |
| 7000 | Cassandra | Apache Cassandra |
| 7001 | Cassandra | Cassandra SSL |
| 8086 | InfluxDB | InfluxDB Time Series |
| 9042 | Cassandra | Cassandra Native |
| 9200 | Elasticsearch | Elasticsearch HTTP |
| 9300 | Elasticsearch | Elasticsearch Transport |
| 27017 | MongoDB | MongoDB Database |

### Web Services
| Port | Service | Description |
|------|---------|-------------|
| 1080 | SOCKS | SOCKS Proxy |
| 3000 | Dev Server | Common development port |
| 3128 | Squid | Squid Proxy |
| 4000 | Dev Server | Common development port |
| 5000 | Dev Server | Flask default |
| 8000 | HTTP Alt | Alternative HTTP |
| 8008 | HTTP Alt | Alternative HTTP |
| 8080 | HTTP Proxy | HTTP Proxy/Alternative |
| 8081 | HTTP Alt | Alternative HTTP |
| 8443 | HTTPS Alt | Alternative HTTPS |
| 8888 | HTTP Alt | Alternative HTTP |
| 9000 | PHP-FPM | PHP FastCGI |

### Remote Access & Management
| Port | Service | Description |
|------|---------|-------------|
| 1194 | OpenVPN | OpenVPN Default |
| 1701 | L2TP | Layer 2 Tunneling Protocol |
| 1723 | PPTP | Point-to-Point Tunneling |
| 2049 | NFS | Network File System |
| 2082 | cPanel | cPanel Control Panel |
| 2083 | cPanel SSL | cPanel Secure |
| 2086 | WHM | Web Host Manager |
| 2087 | WHM SSL | WHM Secure |
| 3389 | RDP | Remote Desktop Protocol |
| 4369 | EPMD | Erlang Port Mapper |
| 5432 | PostgreSQL | PostgreSQL Database |
| 5900 | VNC | Virtual Network Computing |
| 5901-5910 | VNC | VNC Display 1-10 |
| 10050 | Zabbix | Zabbix Agent |
| 10051 | Zabbix | Zabbix Server |

### Messaging & Streaming
| Port | Service | Description |
|------|---------|-------------|
| 1883 | MQTT | Message Queue Telemetry Transport |
| 4222 | NATS | NATS Messaging |
| 5222 | XMPP | XMPP Client |
| 5269 | XMPP | XMPP Server |
| 5672 | AMQP | RabbitMQ |
| 6667 | IRC | Internet Relay Chat |
| 6697 | IRC SSL | IRC Secure |
| 8883 | MQTT SSL | MQTT Secure |
| 9092 | Kafka | Apache Kafka |
| 15672 | RabbitMQ | RabbitMQ Management |
| 51820 | WireGuard | WireGuard VPN |

### Container & Orchestration
| Port | Service | Description |
|------|---------|-------------|
| 2375 | Docker | Docker REST API |
| 2376 | Docker SSL | Docker REST API Secure |
| 2377 | Docker Swarm | Swarm Management |
| 4789 | VXLAN | Docker Overlay Network |
| 6443 | Kubernetes | Kubernetes API Server |
| 7946 | Docker | Container Network Discovery |
| 8472 | Flannel | Kubernetes Flannel VXLAN |
| 10250 | Kubelet | Kubernetes Kubelet API |
| 10251 | Kube-scheduler | Kubernetes Scheduler |
| 10252 | Kube-controller | Kubernetes Controller |

## Dynamic/Private Ports (49152-65535)

These ports are typically used for:
- Ephemeral client connections
- Dynamic service allocation
- Private applications

## Port Ranges by Service Type

### Email Ports
```
SMTP:    25 (plain), 465 (SSL), 587 (STARTTLS)
POP3:    110 (plain), 995 (SSL)
IMAP:    143 (plain), 993 (SSL)
```

### Web Server Ports
```
HTTP:    80, 8080, 8000, 8008, 3000, 5000
HTTPS:   443, 8443
```

### Database Ports
```
Relational:  3306 (MySQL), 5432 (PostgreSQL), 1433 (MSSQL)
NoSQL:       27017 (MongoDB), 6379 (Redis), 9200 (Elastic)
```

### VPN Ports
```
PPTP:    1723 (TCP)
L2TP:    1701 (UDP)
IPSec:   500, 4500 (UDP)
OpenVPN: 1194 (UDP/TCP)
WireGuard: 51820 (UDP)
```

## Security Considerations

### Commonly Attacked Ports
| Port | Service | Risk Level | Common Attacks |
|------|---------|------------|----------------|
| 22 | SSH | High | Brute force, exploits |
| 23 | Telnet | Critical | Clear text passwords |
| 445 | SMB | Critical | Ransomware, worms |
| 1433 | MS SQL | High | SQL injection, brute force |
| 3306 | MySQL | High | SQL injection, brute force |
| 3389 | RDP | Critical | Brute force, BlueKeep |
| 5900 | VNC | High | Weak authentication |

### Ports to Block at Firewall
```
Inbound (typical):
- 135-139 (NetBIOS)
- 445 (SMB)
- 1433-1434 (MS SQL)
- 3389 (RDP) - unless needed
- 5900-5910 (VNC) - unless needed

Outbound (restrictive):
- 25 (SMTP) - prevent spam
- 6667 (IRC) - prevent botnet
- All except explicitly allowed
```

## Quick Port Check Commands

### Check if port is open
```bash
# Local ports
netstat -an | grep :80
ss -tuln | grep :80
lsof -i :80

# Remote ports
nc -zv hostname 80
nmap -p 80 hostname
telnet hostname 80
```

### Common service ports test
```bash
# Web server
curl -I http://hostname:80
curl -I https://hostname:443

# SSH
ssh -p 22 user@hostname

# Database
mysql -h hostname -P 3306
psql -h hostname -p 5432
```