# Data Accuracy Assessment for Internet Visualization

## Executive Summary
This document assesses the accuracy and availability of data sources for real-world internet infrastructure visualization, distinguishing between what can be shown with high confidence versus what must be estimated or simulated.

## Data Availability Tiers

### Tier 1: Highly Accurate & Available (90-100% Accurate)
These data sources are publicly available and highly reliable.

#### Infrastructure Data
| Data Type | Source | Update Frequency | Accuracy | Notes |
|-----------|--------|------------------|----------|-------|
| Submarine cables | TeleGeography | Monthly | 95% | Missing some military/private cables |
| Internet Exchange Points | PeeringDB | Real-time | 98% | Self-reported but comprehensive |
| BGP routing tables | RouteViews, RIPE RIS | Real-time | 100% | Complete for participating ASNs |
| DNS root servers | IANA | Static | 100% | All 13 root servers documented |
| Major cloud regions | AWS, Azure, GCP APIs | Real-time | 100% | Official APIs available |
| IPv4/IPv6 allocations | Regional Internet Registries | Daily | 100% | Authoritative source |
| AS number assignments | IANA, RIRs | Daily | 100% | Complete registry |

#### Performance Metrics
| Data Type | Source | Update Frequency | Accuracy | Notes |
|-----------|--------|------------------|----------|-------|
| Latency measurements | RIPE Atlas | Real-time | 95% | 12,000+ global probes |
| DNS response times | Your own queries | Real-time | 100% | Direct measurement |
| Traceroute paths | Direct measurement | Real-time | 85% | Some hops may not respond |
| IPv6 adoption | Google, APNIC | Daily | 95% | Large sample size |
| Certificate transparency | CT logs | Real-time | 100% | All certificates logged |
| Protocol support | TLS scanner | On-demand | 100% | Can test any server |

### Tier 2: Partially Available/Estimated (50-75% Accurate)
These require interpolation, estimation, or incomplete data.

#### Traffic & Usage Data
| Data Type | Estimation Method | Accuracy | Limitations |
|-----------|------------------|----------|-------------|
| Live traffic volumes | Statistical modeling | 60% | ISPs don't share real data |
| DDoS attack detection | Public feeds + inference | 50% | Only major attacks visible |
| Cable utilization | Industry reports | 40% | Proprietary information |
| CDN cache hit rates | HTTP headers + inference | 70% | Varies by provider |
| Data travel distance | Cable route calculation | 75% | Assumes optimal routing |
| Packet loss rates | Active measurement | 80% | Sample-based |

#### Cost & Environmental Data
| Data Type | Estimation Method | Accuracy | Limitations |
|-----------|------------------|----------|-------------|
| Bandwidth costs | Industry averages | 60% | Highly variable by region |
| Carbon per GB | Research papers | 50% | Based on averages |
| Data center PUE | Published reports | 70% | Self-reported, may be optimistic |
| Renewable energy % | Company reports | 60% | Not independently verified |

### Tier 3: Unavailable/Confidential (0-25% Accurate)
These cannot be accurately determined from public sources.

#### Proprietary/Sensitive Data
| Data Type | Why Unavailable | Alternatives |
|-----------|-----------------|--------------|
| Terrestrial fiber routes | Security sensitive | Show logical connectivity instead |
| ISP internal routing | Trade secrets | Show AS-level paths only |
| Real peering agreements | Under NDA | Show public peering only |
| Actual server locations | Security | Show region/city level |
| User personal traffic | Privacy laws | Only show user's own data |
| Government infrastructure | Classified | Exclude entirely |
| Real-time cable cuts | Delayed reporting | Show historical events |

## Validation Methodology

### How We Verify Accuracy

#### Direct Measurement
```javascript
// Can measure directly
- traceroute to any destination
- DNS query times
- TLS handshake details
- HTTP response headers
- Your bandwidth to test servers
```

#### Cross-Reference Validation
```javascript
// Multiple sources confirm
- Submarine cable routes (3+ sources)
- Data center locations (company + third-party)
- Outage reports (multiple detection systems)
- BGP routes (multiple vantage points)
```

#### Statistical Inference
```javascript
// Educated estimates based on
- Sampling (RIPE Atlas probes)
- Historical patterns
- Industry benchmarks
- Academic research
```

## Implementation Guidelines

### Accuracy Disclosure Best Practices

#### Clear Labeling
```javascript
// Good examples
"Measured latency: 47ms (±2ms)"
"Estimated distance: ~15,000 miles"
"Based on 1,000 sample measurements"
"Data from: CloudFlare Radar (updated hourly)"
```

#### Confidence Indicators
```javascript
// Visual indicators
🟢 High confidence (measured)
🟡 Medium confidence (estimated)
🔴 Low confidence (inferred)
⚫ No data available
```

#### Data Freshness
```javascript
// Always show
"Last updated: 5 minutes ago"
"Historical data from: 2024-01-15"
"Real-time" (WebSocket connected)
"Cached data" (may be stale)
```

### Ethical Considerations

#### Privacy Protection
- Never attempt to show other users' traffic
- Anonymize/aggregate where necessary
- Comply with GDPR/CCPA
- Allow opt-out of tracking

#### Security Responsibility
- Don't reveal sensitive infrastructure details
- Avoid real-time precision that could aid attacks
- Delay certain data (cable cuts, outages)
- Exclude military/government infrastructure

#### Transparency
- Cite all data sources
- Explain estimation methods
- Acknowledge limitations
- Provide methodology documentation

## Recommended Data Stack

### Primary Sources (High Confidence)
```yaml
Infrastructure:
  - TeleGeography: Submarine cables
  - PeeringDB: Interconnection data
  - Hurricane Electric: BGP looking glass
  - RIPE Atlas: Global measurements
  - CAIDA: Internet topology

Performance:
  - M-Lab: Speed tests
  - CloudFlare Radar: Traffic patterns
  - Google Transparency: Certificate data
  - APNIC: IPv6 statistics
```

### Secondary Sources (Medium Confidence)
```yaml
Enrichment:
  - MaxMind: Geolocation
  - Team Cymru: AS data
  - Shodan: Device census
  - GreyNoise: Threat intelligence
  - Internet Archive: Historical data
```

### Estimation Models
```yaml
Calculations:
  - Great-circle distance for cable routes
  - Industry average costs ($0.02-0.08 per GB)
  - Standard PUE values (1.2-2.0)
  - Carbon intensity (5-500g CO2/kWh by region)
```

## Conclusion

### What We Can Accurately Show
- Physical infrastructure locations (cables, IXPs, data centers)
- Logical routing (BGP, DNS)
- Personal measurements (your latency, traceroute)
- Protocol behavior (TLS, HTTP)
- Historical events and trends

### What We Must Estimate
- Real-time traffic volumes
- Actual costs
- Environmental impact
- Some geographic paths
- Utilization rates

### What We Cannot Show
- Private user data
- Proprietary routing
- Classified infrastructure
- Real-time attacks (without delay)
- Exact server locations

## Recommendation
Focus on Tier 1 data for core functionality, clearly label Tier 2 estimations, and avoid claiming to show Tier 3 data. This approach maintains credibility while still providing valuable insights into internet infrastructure.