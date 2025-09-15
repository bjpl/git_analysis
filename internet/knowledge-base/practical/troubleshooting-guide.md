# Network Troubleshooting Guide

## Systematic Troubleshooting Approach

### OSI Layer Troubleshooting (Bottom-Up)
```
1. Physical → Cable connected? Link lights?
2. Data Link → ARP working? Switch issues?
3. Network → Can ping gateway? Routing?
4. Transport → Port open? Firewall?
5. Session → Session established?
6. Presentation → Encoding issues?
7. Application → Application-specific problems?
```

## Common Network Issues and Solutions

### No Internet Connection

#### Diagnostic Flow
```
1. Check physical connection
   └─ Cable plugged in?
   └─ WiFi connected?
   
2. Check link layer
   └─ ipconfig/ifconfig - IP assigned?
   └─ No IP? → DHCP issue
   
3. Check network layer  
   └─ ping 127.0.0.1 (loopback)
   └─ ping gateway
   └─ ping 8.8.8.8 (public IP)
   
4. Check DNS
   └─ nslookup google.com
   └─ ping google.com
   
5. Check application
   └─ Browser specific?
   └─ Firewall blocking?
```

### Slow Network Performance

#### Performance Diagnostics
| Test | Command | Indicates |
|------|---------|-----------|
| Latency | `ping -t` | Network delay, packet loss |
| Bandwidth | `iperf3` | Throughput capacity |
| Path | `traceroute/tracert` | Routing issues, slow hops |
| DNS | `dig +stats` | DNS resolution time |
| Packet capture | `tcpdump/wireshark` | Retransmissions, errors |

#### Common Causes
1. **High latency** → Distance, congestion, routing
2. **Packet loss** → Bad cable, interference, congestion
3. **Low bandwidth** → Throttling, congestion, QoS
4. **DNS delays** → Slow resolver, DNSSEC validation
5. **TCP issues** → Small window, retransmissions

## Command-Line Tools Reference

### Windows Commands
```bash
# Basic connectivity
ping -t 8.8.8.8              # Continuous ping
ping -l 1472 -f 8.8.8.8      # MTU discovery

# Path analysis
tracert google.com           # Trace route
pathping google.com          # Combines ping and tracert

# DNS troubleshooting
nslookup google.com          # DNS lookup
nslookup google.com 8.8.8.8  # Use specific DNS
ipconfig /flushdns           # Clear DNS cache
ipconfig /displaydns         # Show DNS cache

# Network configuration
ipconfig /all                # Show all adapters
ipconfig /release            # Release DHCP
ipconfig /renew              # Renew DHCP
arp -a                       # Show ARP table
route print                  # Show routing table
netstat -an                  # Show connections
netstat -r                   # Show routes
netsh int ip reset          # Reset TCP/IP stack
```

### Linux/Mac Commands
```bash
# Basic connectivity
ping -c 10 8.8.8.8           # Send 10 pings
ping -s 1472 -M do 8.8.8.8   # MTU discovery (Linux)
ping -D -s 1472 8.8.8.8      # MTU discovery (Mac)

# Path analysis
traceroute google.com        # Trace route
mtr google.com               # Combined trace + stats

# DNS troubleshooting
dig google.com               # Detailed DNS lookup
dig +trace google.com        # Full resolution path
dig +short google.com        # Simple output
host google.com              # Basic lookup
nslookup google.com          # Traditional lookup
systemd-resolve --flush-caches  # Clear cache (systemd)

# Network configuration
ifconfig -a                  # Show interfaces (deprecated)
ip addr show                 # Show IP addresses
ip route show                # Show routes
arp -n                       # Show ARP table
ss -tuln                     # Show listening ports
netstat -tuln                # Alternative to ss
sudo tcpdump -i any         # Packet capture
```

## Specific Protocol Troubleshooting

### HTTP/HTTPS Issues

#### Using curl for Diagnosis
```bash
# Basic request
curl -I https://example.com              # Headers only

# Detailed timing
curl -w "@curl-format.txt" -o /dev/null -s https://example.com

# curl-format.txt:
time_namelookup:  %{time_namelookup}s\n
time_connect:  %{time_connect}s\n  
time_appconnect:  %{time_appconnect}s\n
time_pretransfer:  %{time_pretransfer}s\n
time_redirect:  %{time_redirect}s\n
time_starttransfer:  %{time_starttransfer}s\n
time_total:  %{time_total}s\n

# TLS debugging
curl -v https://example.com              # Verbose (shows TLS handshake)
openssl s_client -connect example.com:443  # TLS details
```

### DNS Issues

#### Common DNS Problems
| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| NXDOMAIN | Domain doesn't exist | Check spelling, wait for propagation |
| SERVFAIL | DNS server error | Try different resolver |
| Timeout | Network issue | Check connectivity to DNS |
| Wrong IP | Cached/stale | Flush cache, check TTL |
| Slow resolution | Distant resolver | Use closer/faster DNS |

#### DNS Debugging Commands
```bash
# Query specific record types
dig A example.com       # IPv4 address
dig AAAA example.com    # IPv6 address
dig MX example.com      # Mail servers
dig NS example.com      # Name servers
dig ANY example.com     # All records

# Check DNS propagation
dig @8.8.8.8 example.com    # Google DNS
dig @1.1.1.1 example.com    # Cloudflare DNS
dig @208.67.222.222 example.com  # OpenDNS

# Trace delegation
dig +trace example.com   # Full resolution path
```

### TCP Connection Issues

#### TCP State Diagnostics
```bash
# Check connection states
netstat -tan | grep :443     # HTTPS connections
ss -tan state established    # Established only

# Common states and meanings:
LISTEN      - Waiting for connections
SYN_SENT    - Connection initiated
SYN_RECV    - Connection request received
ESTABLISHED - Active connection
FIN_WAIT1   - Closing, waiting for ACK
FIN_WAIT2   - Closing, waiting for FIN
TIME_WAIT   - Closed, waiting for stray packets
CLOSE_WAIT  - Remote closed, local hasn't
```

## Packet Loss Diagnosis

### Identifying Packet Loss
```bash
# Basic packet loss test
ping -c 100 target.com | grep loss

# MTR for continuous monitoring
mtr --report --report-cycles 100 target.com

# Check different packet sizes
for size in 64 512 1024 1472; do
    echo "Testing size $size"
    ping -c 20 -s $size target.com
done
```

### Common Packet Loss Causes
1. **Physical layer** - Bad cable, interference
2. **Congestion** - Buffer overflow, QoS drops
3. **MTU issues** - Fragmentation problems
4. **Firewall/IDS** - Security device dropping
5. **Routing loops** - TTL expiration

## Performance Bottleneck Analysis

### Bandwidth Testing
```bash
# Install iperf3 on both ends
# Server:
iperf3 -s

# Client:
iperf3 -c server_ip          # TCP test
iperf3 -c server_ip -u -b 100M  # UDP test
iperf3 -c server_ip -R       # Reverse mode
iperf3 -c server_ip -P 10    # 10 parallel streams
```

### Latency Analysis
```bash
# Measure different types of latency
# Network latency
ping -c 100 target | grep avg

# Application latency  
time curl -o /dev/null -s https://example.com

# DNS latency
time dig example.com

# TCP handshake time
time nc -zv example.com 443
```

## Wireshark Filters for Common Issues

### Useful Display Filters
```
# TCP problems
tcp.analysis.flags          # All TCP problems
tcp.analysis.retransmission # Retransmissions
tcp.analysis.duplicate_ack  # Duplicate ACKs
tcp.analysis.lost_segment   # Lost segments
tcp.flags.reset == 1        # RST packets

# HTTP issues
http.response.code >= 400   # HTTP errors
http.time > 1               # Slow HTTP responses

# DNS issues
dns.flags.rcode != 0        # DNS errors
dns.time > 0.5              # Slow DNS

# General issues
icmp                        # All ICMP (includes errors)
frame.time_delta > 1        # Gaps > 1 second
```

## Quick Fixes for Common Problems

### Reset Network Stack
```bash
# Windows
netsh winsock reset
netsh int ip reset
ipconfig /flushdns

# Linux
sudo systemctl restart NetworkManager
sudo systemctl restart systemd-resolved
sudo ip addr flush dev eth0
sudo systemctl restart networking

# Mac
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### Common Router Issues
1. **Reboot router** - Clears memory, resets connections
2. **Update firmware** - Fixes bugs, security issues
3. **Change DNS servers** - Use 8.8.8.8, 1.1.1.1
4. **Disable WPS** - Security vulnerability
5. **Check DHCP pool** - Might be exhausted
6. **Review port forwards** - May conflict