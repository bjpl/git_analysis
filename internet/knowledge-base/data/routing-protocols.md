# Routing Protocols Comprehensive Reference

## Interior Gateway Protocols (IGP)

### Distance Vector Protocols

#### RIP (Routing Information Protocol)
| Version | Metric | Max Hops | Convergence | Use Case |
|---------|--------|----------|-------------|----------|
| **RIPv1** | Hop count | 15 | 180-240s | Legacy, classful |
| **RIPv2** | Hop count | 15 | 180-240s | Small networks, VLSM |
| **RIPng** | Hop count | 15 | 180-240s | IPv6 small networks |

**Features**:
- Simple configuration
- Slow convergence
- Count-to-infinity problem
- Split horizon for loop prevention
- UDP port 520 (RIPv2), 521 (RIPng)

#### EIGRP (Enhanced Interior Gateway Routing Protocol)
**Type**: Advanced Distance Vector  
**Algorithm**: DUAL (Diffusing Update Algorithm)  
**Convergence**: 1-5 seconds  
**Metric**: Composite (Bandwidth, Delay, Load, Reliability)

| Feature | Description | Benefit |
|---------|-------------|---------|
| Feasible Successors | Backup routes | Instant failover |
| Unequal Cost Load Balancing | Variance command | Better bandwidth usage |
| Stub Routing | Reduce query scope | Improved stability |
| Route Summarization | Automatic/manual | Reduced routing table |

**Administrative Distance**:
- Internal: 90
- External: 170
- Summary: 5

### Link State Protocols

#### OSPF (Open Shortest Path First)
**Algorithm**: Dijkstra's Shortest Path First  
**Metric**: Cost (10^8/bandwidth)  
**Areas**: Hierarchical design with Area 0 backbone

| Area Type | Description | LSA Types Allowed |
|-----------|-------------|-------------------|
| **Backbone (Area 0)** | Core area | All types |
| **Standard** | Normal area | All types |
| **Stub** | No external routes | 1,2,3,4 |
| **Totally Stubby** | No external or inter-area | 1,2,3 |
| **NSSA** | Stub with external capability | 1,2,3,4,7 |
| **Totally NSSA** | NSSA with no inter-area | 1,2,3,7 |

**LSA Types**:
1. Router LSA
2. Network LSA
3. Summary LSA (Inter-area)
4. Summary ASBR LSA
5. External LSA
6. Group Membership LSA
7. NSSA External LSA

**Convergence Process**:
1. Hello packets (10s LAN, 30s WAN)
2. Dead timer (4x Hello)
3. DR/BDR election on multi-access
4. LSA flooding
5. SPF calculation

#### IS-IS (Intermediate System to Intermediate System)
**Type**: Link State  
**Levels**: Two-level hierarchy (L1 intra-area, L2 inter-area)  
**Protocol**: Runs directly on Layer 2

| Feature | OSPF | IS-IS |
|---------|------|-------|
| Runs on | IP | Layer 2 |
| Hierarchy | Areas | Levels |
| Scalability | Good | Excellent |
| Convergence | 5-10s | 5-10s |
| Adoption | Enterprise | Service Provider |

## Exterior Gateway Protocols (EGP)

### BGP (Border Gateway Protocol)
**Version**: BGP-4 (current standard)  
**Type**: Path Vector  
**Port**: TCP 179  
**Use**: Internet routing between Autonomous Systems

#### BGP Path Selection Process
1. **Weight** (Cisco): Highest (local to router)
2. **Local Preference**: Highest (within AS)
3. **Self-originated**: Prefer own routes
4. **AS Path**: Shortest
5. **Origin**: IGP > EGP > Incomplete
6. **MED**: Lowest (between AS pairs)
7. **eBGP > iBGP**: External preferred
8. **IGP Metric**: Lowest to next hop
9. **Oldest Route**: Most stable
10. **Router ID**: Lowest

#### BGP Attributes

| Attribute | Type | Description | Scope |
|-----------|------|-------------|-------|
| **AS_PATH** | Well-known mandatory | AS sequence | Global |
| **NEXT_HOP** | Well-known mandatory | Next hop IP | Per-hop |
| **LOCAL_PREF** | Well-known discretionary | Preference within AS | AS-wide |
| **MED** | Optional non-transitive | Metric between AS | Adjacent AS |
| **COMMUNITY** | Optional transitive | Route tagging | Policy-based |
| **ORIGIN** | Well-known mandatory | Route origin | Global |

#### BGP Types
- **eBGP**: Between different AS (AD: 20)
- **iBGP**: Within same AS (AD: 200)
- **MP-BGP**: Multi-protocol (IPv6, VPNv4, etc.)

## Multicast Routing Protocols

| Protocol | Type | Mode | Use Case |
|----------|------|------|----------|
| **PIM-SM** | Sparse Mode | Pull model | Most multicast |
| **PIM-DM** | Dense Mode | Push model | Small, dense groups |
| **DVMRP** | Distance Vector | Flood & Prune | Legacy |
| **MOSPF** | Link State | OSPF extension | Single OSPF domain |

## Administrative Distance Comparison

| Route Source | Default AD | Trustworthiness |
|--------------|------------|-----------------|
| Connected | 0 | Most trusted |
| Static | 1 | Very trusted |
| EIGRP Summary | 5 | High trust |
| eBGP | 20 | External routes |
| EIGRP Internal | 90 | Internal dynamic |
| OSPF | 110 | Standard IGP |
| IS-IS | 115 | Alternative IGP |
| RIP | 120 | Less preferred |
| EIGRP External | 170 | External to EIGRP |
| iBGP | 200 | Internal BGP |
| Unknown | 255 | Never installed |

## Modern Routing Technologies

### Segment Routing
**Concept**: Source routing with segment IDs  
**Benefits**: Simplified MPLS, traffic engineering  
**Types**:
- SR-MPLS: MPLS data plane
- SRv6: IPv6 data plane

### Software-Defined Routing

| Technology | Description | Use Case |
|------------|-------------|----------|
| **SDN** | Centralized control plane | Data center |
| **SD-WAN** | Overlay WAN | Enterprise WAN |
| **LISP** | Location/ID separation | Mobility |
| **VXLAN** | L2 over L3 overlay | Data center |
| **EVPN** | BGP-based L2VPN | Data center fabric |

## First Hop Redundancy Protocols

| Protocol | Vendor | Load Balancing | Convergence | Groups |
|----------|--------|---------------|-------------|--------|
| **HSRP** | Cisco | No (Active/Standby) | 3-10s | 256 |
| **VRRP** | Standard | No (Master/Backup) | 3-4s | 255 |
| **GLBP** | Cisco | Yes (Active/Active) | 3-10s | 1024 |

## Routing Protocol Selection Criteria

### By Network Size
- **Small (< 50 routers)**: RIP, EIGRP, OSPF single area
- **Medium (50-500)**: OSPF multi-area, EIGRP
- **Large (500+)**: OSPF, IS-IS, BGP
- **Internet Scale**: BGP only

### By Requirements
| Requirement | Best Choice | Alternative |
|-------------|------------|-------------|
| Fast convergence | EIGRP | OSPF |
| Vendor neutral | OSPF | IS-IS |
| Simple setup | RIP | Static |
| Traffic engineering | MPLS-TE | Segment Routing |
| Multi-vendor | OSPF | IS-IS |
| Service Provider | IS-IS | OSPF |
| Internet connectivity | BGP | Static + NAT |

## Convergence Times

| Protocol | Detection | Convergence | Total Time |
|----------|-----------|-------------|------------|
| **Static** | N/A | Immediate | 0s |
| **EIGRP** | 5s (Hello) | <1s | 1-5s |
| **OSPF** | 10-40s | 5s SPF | 5-45s |
| **IS-IS** | 10-30s | 5s SPF | 5-35s |
| **BGP** | 60-180s | 30s+ | 30-180s |
| **RIP** | 180s | 180-240s | 180-240s |

## Best Practices

### Design Principles
1. **Hierarchy**: Use areas/levels for scalability
2. **Summarization**: Reduce routing table size
3. **Redundancy**: Multiple paths and protocols
4. **Authentication**: Enable on all protocols
5. **Filtering**: Control route propagation

### Optimization Techniques
- **Route Summarization**: Reduce table size
- **Stub Areas**: Limit LSA propagation
- **Route Filtering**: Control advertisements
- **Timer Tuning**: Balance speed vs stability
- **BFD**: Sub-second failure detection

### Security Measures
| Protocol | Authentication | Encryption |
|----------|---------------|------------|
| OSPF | MD5, SHA | IPSec |
| EIGRP | MD5, SHA | IPSec |
| BGP | MD5, TCP-AO | IPSec, GTSM |
| IS-IS | MD5, SHA | Layer 2 security |
| RIP | MD5 | IPSec |