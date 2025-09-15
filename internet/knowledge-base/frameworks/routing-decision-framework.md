# Routing Decision Framework

## Packet Forwarding Decision Tree

```
Packet Arrives at Router
    ↓
Is destination local?
    Yes → Deliver directly (ARP for MAC)
    No ↓
    
Check routing table
    ↓
Longest prefix match?
    Found → Forward to next hop
    Not found ↓
    
Default route exists?
    Yes → Forward to default gateway
    No → Drop packet (ICMP unreachable)
```

## BGP Path Selection Algorithm

### Selection Order (Cisco)
1. **Weight** (Highest) - Local to router
2. **Local Preference** (Highest) - Within AS
3. **Self-originated** - Routes you advertise
4. **AS Path** (Shortest) - Fewer AS hops
5. **Origin** (IGP > EGP > Incomplete)
6. **MED** (Lowest) - Multi-Exit Discriminator
7. **External > Internal** - eBGP over iBGP
8. **IGP Metric** (Lowest) - Cost to next hop
9. **Oldest Route** - Stability preference
10. **Router ID** (Lowest) - Tie breaker

## OSPF Route Calculation

### Dijkstra's Algorithm Process
```
1. Initialize:
   - Set distance to self = 0
   - Set distance to all others = infinity
   - Mark all nodes unvisited

2. For current node:
   - Calculate tentative distances to neighbors
   - Compare with current assigned values
   - Keep smaller value

3. Mark current as visited
4. Select unvisited node with smallest distance
5. Repeat until all visited
```

### OSPF Metrics
- **Cost** = Reference Bandwidth / Interface Bandwidth
- Default reference: 100 Mbps
- Example: 1 Gbps link = 100/1000 = 0.1 (rounds to 1)

## Routing Protocol Comparison

| Protocol | Type | Metric | Convergence | Scale | Use Case |
|----------|------|--------|-------------|-------|----------|
| RIP | Distance Vector | Hop count | Slow (minutes) | Small (<15 hops) | Legacy/Simple |
| OSPF | Link State | Bandwidth | Fast (seconds) | Large | Enterprise |
| IS-IS | Link State | Configurable | Fast | Very Large | ISP |
| EIGRP | Hybrid | Composite | Very Fast | Large | Cisco networks |
| BGP | Path Vector | Attributes | Slow (minutes) | Internet-scale | Between AS |

## Route Types and Preference

### Administrative Distance (Cisco)
| Route Source | AD Value | Trust Level |
|--------------|----------|-------------|
| Connected | 0 | Most trusted |
| Static | 1 | Manually configured |
| EIGRP Summary | 5 | - |
| eBGP | 20 | External BGP |
| EIGRP Internal | 90 | - |
| OSPF | 110 | - |
| IS-IS | 115 | - |
| RIP | 120 | - |
| EIGRP External | 170 | - |
| iBGP | 200 | Internal BGP |
| Unknown | 255 | Never used |

## Route Aggregation Strategy

### Benefits
- Smaller routing tables
- Faster lookups
- Reduced update traffic
- Better stability

### Aggregation Rules
```
Can aggregate:
192.168.0.0/24
192.168.1.0/24  → 192.168.0.0/23
192.168.2.0/24
192.168.3.0/24  → 192.168.2.0/23
                → 192.168.0.0/22 (all four)

Cannot aggregate (non-contiguous):
192.168.1.0/24
192.168.3.0/24  → Must advertise separately
```

## Traffic Engineering Techniques

### Load Balancing Methods
1. **Per-packet**: Round-robin (can cause reordering)
2. **Per-flow**: Hash-based (maintains order)
3. **ECMP**: Equal Cost Multi-Path
4. **Unequal cost**: EIGRP variance

### BGP Traffic Engineering
- **Outbound**: Local preference, AS path prepending
- **Inbound**: MED, AS path prepending, communities
- **Selective advertisement**: Advertise different prefixes to different peers

## Troubleshooting Decision Flow

```
1. Local connectivity?
   ping default gateway
   
2. DNS resolution?
   nslookup/dig
   
3. Route exists?
   traceroute/tracert
   
4. Correct path?
   Check routing table
   
5. Return path?
   Asymmetric routing check
   
6. MTU issues?
   ping with DF bit
   
7. Firewall/ACL?
   Check drops/blocks
```

## Routing Loop Prevention

### Mechanisms by Protocol
- **RIP**: Maximum hop count (15)
- **OSPF**: Link state database consistency
- **EIGRP**: DUAL algorithm, feasible successors
- **BGP**: AS path (won't accept routes containing own AS)
- **General**: Split horizon, route poisoning, hold-down timers