# Performance Metrics Reference Guide

## Core Web Vitals

### Largest Contentful Paint (LCP)
**Measures**: Loading performance - when main content loads  
**Unit**: Seconds

| Rating | Threshold | User Experience |
|--------|-----------|-----------------|
| Good | ≤ 2.5s | Fast loading |
| Needs Improvement | 2.5s - 4.0s | Moderate |
| Poor | > 4.0s | Slow loading |

**Key Factors**:
- Server response time (TTFB)
- CSS blocking time
- Resource load time
- Client-side rendering

**Optimization Strategies**:
- Server: Optimize TTFB, enable compression, use CDN
- Resources: Preload critical resources, optimize images, remove unused CSS
- Rendering: Avoid heavy client-side rendering, minimize JavaScript execution

### First Input Delay (FID)
**Measures**: Interactivity - time to respond to first interaction  
**Unit**: Milliseconds

| Rating | Threshold | User Experience |
|--------|-----------|-----------------|
| Good | ≤ 100ms | Responsive |
| Needs Improvement | 100ms - 300ms | Noticeable delay |
| Poor | > 300ms | Sluggish |

**Key Factors**:
- JavaScript execution time
- Main thread blocking
- Third-party scripts

**Optimization Strategies**:
- JavaScript: Code splitting, defer non-critical JS, minimize execution
- Workers: Use Web Workers, offload heavy computation
- Third-party: Lazy load third-party scripts, reduce their impact

### Cumulative Layout Shift (CLS)
**Measures**: Visual stability - unexpected layout shifts  
**Unit**: Score (unitless)

| Rating | Threshold | User Experience |
|--------|-----------|-----------------|
| Good | ≤ 0.1 | Stable |
| Needs Improvement | 0.1 - 0.25 | Some shifting |
| Poor | > 0.25 | Unstable |

**Common Causes**:
- Images without dimensions
- Ads/embeds without reserved space
- Dynamically injected content
- Web fonts causing FOIT/FOUT

**Prevention**:
- Always set width/height on images and video
- Reserve space for ads and embeds
- Avoid inserting content above existing content
- Use font-display: optional or swap

## Other Key Metrics

### Time to First Byte (TTFB)
**Measures**: Server response time  
**Unit**: Milliseconds

| Rating | Threshold | Impact |
|--------|-----------|--------|
| Good | ≤ 200ms | Fast server response |
| Acceptable | 200ms - 500ms | Moderate |
| Poor | > 500ms | Slow server |

**Optimization**:
- Use CDN for geographic distribution
- Optimize database queries
- Implement server-side caching
- Upgrade hosting infrastructure

### First Contentful Paint (FCP)
**Measures**: When first content appears  
**Unit**: Seconds

| Rating | Threshold | Perception |
|--------|-----------|------------|
| Good | ≤ 1.8s | Fast |
| Needs Improvement | 1.8s - 3.0s | Moderate |
| Poor | > 3.0s | Slow |

### Time to Interactive (TTI)
**Measures**: When page becomes fully interactive  
**Unit**: Seconds

| Rating | Threshold | User Impact |
|--------|-----------|-------------|
| Good | ≤ 3.8s | Quick to use |
| Needs Improvement | 3.8s - 7.3s | Delayed interaction |
| Poor | > 7.3s | Frustrating |

### Total Blocking Time (TBT)
**Measures**: Total time main thread was blocked  
**Unit**: Milliseconds

| Rating | Threshold | Experience |
|--------|-----------|------------|
| Good | ≤ 200ms | Responsive |
| Needs Improvement | 200ms - 600ms | Some lag |
| Poor | > 600ms | Unresponsive |

## Network Metrics

### Round Trip Time (RTT)
**Measures**: Network latency

| Connection | Good | Acceptable | Poor |
|------------|------|------------|------|
| Local | < 1ms | 1-5ms | > 5ms |
| Regional | < 20ms | 20-50ms | > 50ms |
| Continental | < 80ms | 80-150ms | > 150ms |
| Intercontinental | < 150ms | 150-300ms | > 300ms |

### Bandwidth Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Throughput | Actual data transfer rate | 80%+ of connection speed |
| Packet Loss | Lost packets percentage | < 0.1% |
| Jitter | Variation in latency | < 30ms |
| Buffer Bloat | Excess buffering latency | < 100ms |

## Application Metrics

### API Performance

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Response Time | < 200ms | 200ms - 1s | > 1s |
| Error Rate | < 0.1% | 0.1% - 1% | > 1% |
| Throughput | > 1000 req/s | 100-1000 req/s | < 100 req/s |

### Database Performance

| Operation | Good | Acceptable | Poor |
|-----------|------|------------|------|
| Simple Query | < 10ms | 10-100ms | > 100ms |
| Complex Query | < 100ms | 100ms - 1s | > 1s |
| Write Operation | < 50ms | 50-200ms | > 200ms |
| Connection Pool | < 5ms | 5-20ms | > 20ms |

## Mobile Specific Metrics

### Mobile Network Performance

| Network | Latency | Bandwidth | Packet Loss |
|---------|---------|-----------|-------------|
| 5G | 1-10ms | 100+ Mbps | < 0.01% |
| 4G LTE | 20-40ms | 10-50 Mbps | < 0.1% |
| 3G | 100-500ms | 1-5 Mbps | < 1% |
| 2G | 500ms+ | < 1 Mbps | > 1% |

### Mobile Web Vitals Adjustments

| Metric | Desktop | Mobile | Reason |
|--------|---------|--------|--------|
| LCP | 2.5s | 4.0s | Slower networks |
| FID | 100ms | 100ms | Same expectation |
| CLS | 0.1 | 0.1 | Same stability needed |
| TTI | 3.8s | 5.0s | Limited CPU |

## Real User Monitoring (RUM) Percentiles

| Percentile | Meaning | Use Case |
|------------|---------|----------|
| P50 (Median) | 50% of users | Typical experience |
| P75 | 75% of users | Core Web Vitals threshold |
| P90 | 90% of users | Performance budget |
| P95 | 95% of users | Edge case monitoring |
| P99 | 99% of users | Worst case scenario |

## Performance Budgets

### Resource Budgets

| Resource Type | Mobile | Desktop |
|---------------|--------|---------|
| HTML | < 50 KB | < 100 KB |
| CSS | < 50 KB | < 100 KB |
| JavaScript | < 200 KB | < 300 KB |
| Images | < 500 KB | < 1 MB |
| Fonts | < 100 KB | < 200 KB |
| Total | < 1 MB | < 2 MB |

### Metric Budgets

| Metric | Budget | Alert Threshold |
|--------|--------|-----------------|
| LCP | < 2.5s | > 3.0s |
| FID | < 100ms | > 200ms |
| CLS | < 0.1 | > 0.15 |
| TTFB | < 200ms | > 400ms |
| FCP | < 1.8s | > 2.5s |

## Monitoring Tools

### Synthetic Monitoring
- **Lighthouse**: Lab testing and CI/CD integration
- **WebPageTest**: Detailed performance analysis
- **GTmetrix**: Page speed insights
- **Pingdom**: Uptime and performance

### Real User Monitoring
- **Google Analytics**: Core Web Vitals tracking
- **New Relic**: Application performance monitoring
- **Datadog**: Full-stack monitoring
- **Sentry**: Error and performance tracking

### Performance APIs

```javascript
// Navigation Timing
performance.timing.loadEventEnd - performance.timing.navigationStart

// Resource Timing
performance.getEntriesByType('resource')

// User Timing
performance.mark('myMark')
performance.measure('myMeasure', 'startMark', 'endMark')

// Paint Timing
performance.getEntriesByType('paint')

// Layout Shift
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Layout shift:', entry.value)
  }
}).observe({entryTypes: ['layout-shift']})
```

## Best Practices

### Measurement Strategy
1. Set performance budgets
2. Monitor both lab and field data
3. Track percentiles, not just averages
4. Alert on degradation
5. Regular performance audits

### Optimization Priority
1. **Core Web Vitals** - Direct ranking impact
2. **TTFB** - Foundation for all metrics
3. **Resource optimization** - Broad improvement
4. **Third-party scripts** - Often biggest impact
5. **Progressive enhancement** - Resilient performance