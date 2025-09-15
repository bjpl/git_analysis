# CDN Technologies Reference

## CDN Architecture

### Core Components

#### Edge Servers
- **Description**: Servers at network edge serving cached content
- **Locations**: 100-300 Points of Presence (PoPs) globally
- **Capacity**: 10-100 Gbps per server
- **Storage**: 
  - SSD/NVMe for hot content
  - HDD for warm content
- **Benefits**:
  - Low latency (< 50ms to end users)
  - High throughput
  - Built-in redundancy

#### Origin Servers
- **Description**: Source servers with original content
- **Protection**: Origin shield layer prevents overload
- **Connection**: Persistent connections from CDN
- **Optimization**: Connection pooling, keep-alive

#### Points of Presence (PoPs)
- **Components**:
  - Multiple edge servers
  - Routing equipment
  - Cache storage systems
- **Location Tiers**:
  - **Tier 1**: Major cities and Internet Exchange Points
  - **Tier 2**: Regional hubs
  - **Tier 3**: Metro areas

### CDN Topologies

| Topology | Description | Benefits | Drawbacks |
|----------|-------------|----------|-----------|
| Scattered | Many small PoPs | Wide coverage | Lower cache hit rates |
| Consolidated | Fewer large PoPs | Better cache efficiency | Higher latency for some |
| Hybrid | Mix of large and small PoPs | Balanced coverage and efficiency | More complex management |

## Caching Strategies

### Cache Control Headers

| Header | Purpose | Example |
|--------|---------|---------|
| max-age | Time to cache in seconds | max-age=3600 |
| s-maxage | CDN-specific cache time | s-maxage=86400 |
| no-cache | Validate before use | no-cache |
| no-store | Never cache | no-store |
| public | Can be cached by CDN | public |
| private | Browser cache only | private |
| must-revalidate | Check when stale | must-revalidate |
| immutable | Never changes | immutable |

### Cache Policies

#### Time-Based
- **TTL (Time To Live)**: Fixed expiration time
- **Adaptive TTL**: Adjust based on content popularity
- **Grace Period**: Serve stale while revalidating

#### Content-Based
- **Static Content**: Long TTL (days to months)
- **Dynamic Content**: Short TTL (seconds to minutes)
- **API Responses**: Varies by endpoint

#### Invalidation Methods
- **Purge**: Immediate removal
- **Soft Purge**: Mark as stale
- **Surrogate Keys**: Tag-based invalidation

## Performance Features

### Optimization Techniques

| Feature | Description | Performance Impact |
|---------|-------------|-------------------|
| Compression | Gzip/Brotli encoding | 60-80% size reduction |
| Minification | Remove whitespace | 10-30% size reduction |
| Image Optimization | Format conversion, resizing | 30-70% size reduction |
| HTTP/2 Push | Proactive resource sending | 200-500ms saved |
| Connection Coalescing | Reuse TCP connections | 100-300ms saved |

### Advanced Features

#### Edge Computing
- **Edge Workers**: JavaScript at edge locations
- **Processing**: 50-200ms latency reduction
- **Use Cases**:
  - A/B testing
  - Authentication
  - API aggregation
  - Content personalization

#### Load Balancing
- **Methods**:
  - Round-robin
  - Least connections
  - Geographic
  - Performance-based
- **Health Checks**: Automatic failover
- **Session Affinity**: Sticky sessions

## Security Features

### DDoS Protection

| Attack Type | Mitigation | Layer |
|-------------|------------|-------|
| Volume-based | Rate limiting, blackholing | Network (L3/L4) |
| Protocol | SYN cookies, connection limits | Transport (L4) |
| Application | WAF rules, CAPTCHA | Application (L7) |

### Web Application Firewall (WAF)

| Rule Type | Purpose | Examples |
|-----------|---------|----------|
| OWASP Core | Common vulnerabilities | SQL injection, XSS |
| Custom Rules | Site-specific | Business logic |
| Rate Limiting | Prevent abuse | API throttling |
| Geo-blocking | Regional restrictions | Country-based |
| Bot Management | Filter bot traffic | Good vs bad bots |

### SSL/TLS Features
- **Free Certificates**: Let's Encrypt integration
- **Custom Certificates**: BYO certificates
- **SNI Support**: Multiple domains
- **OCSP Stapling**: Faster verification
- **Perfect Forward Secrecy**: Enhanced security

## Content Delivery Patterns

### Static Content
- **Assets**: Images, CSS, JavaScript
- **Cache Duration**: Days to months
- **Invalidation**: Version in filename

### Dynamic Content
- **Caching**: Edge Side Includes (ESI)
- **Personalization**: Edge computing
- **Cache Key**: Include user segments

### Video Streaming
- **Protocols**:
  - HLS (HTTP Live Streaming)
  - DASH (Dynamic Adaptive Streaming)
  - Progressive download
- **Features**:
  - Adaptive bitrate
  - Segment caching
  - Origin shield

### API Acceleration
- **Caching**: Response caching
- **Compression**: JSON compression
- **Connection**: Keep-alive pools
- **Routing**: Anycast for lowest latency

## Major CDN Providers

| Provider | PoPs | Capacity | Specialization |
|----------|------|----------|----------------|
| Cloudflare | 300+ | 172 Tbps | Security + Performance |
| Akamai | 350+ | 250 Tbps | Enterprise, Media |
| Fastly | 60+ | 130 Tbps | Real-time, Edge compute |
| Amazon CloudFront | 450+ | 225 Tbps | AWS integration |
| Google Cloud CDN | 140+ | 100 Tbps | GCP integration |
| Microsoft Azure CDN | 130+ | 165 Tbps | Azure integration |

## Performance Metrics

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Cache Hit Ratio | % served from cache | > 90% |
| Origin Offload | % traffic not hitting origin | > 95% |
| TTFB | Time to First Byte | < 200ms |
| Bandwidth Savings | Reduction in origin bandwidth | > 80% |
| Request Rate | Requests per second | Varies |

### Monitoring
- **Real User Monitoring (RUM)**: Actual user experience
- **Synthetic Monitoring**: Proactive testing
- **Log Analysis**: Access patterns
- **Alert Thresholds**: Performance degradation

## Cost Optimization

### Pricing Models

| Model | Description | Best For |
|-------|-------------|----------|
| Bandwidth | Pay per GB transferred | Predictable traffic |
| Requests | Pay per 10k requests | High cache ratio |
| Committed | Fixed monthly rate | Stable, high volume |
| Hybrid | Mix of bandwidth and requests | Balanced usage |

### Optimization Strategies
- **Increase Cache Hit Ratio**: Better cache headers
- **Optimize Images**: Reduce transfer size
- **Enable Compression**: Reduce bandwidth
- **Use Origin Shield**: Reduce origin costs
- **Regional Caching**: Cache closer to users