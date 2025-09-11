# HTTP Status Codes Reference

## Status Code Categories

| Range | Category | Description |
|-------|----------|-------------|
| 1xx | Informational | Request received, continuing process |
| 2xx | Success | Request successfully received, understood, and accepted |
| 3xx | Redirection | Further action needed to complete request |
| 4xx | Client Error | Request contains bad syntax or cannot be fulfilled |
| 5xx | Server Error | Server failed to fulfill valid request |

## 1xx Informational Responses

| Code | Name | Description | Common Usage |
|------|------|-------------|--------------|
| 100 | Continue | Client should continue request | Large POST requests |
| 101 | Switching Protocols | Server switching protocols | WebSocket upgrade |
| 102 | Processing | Server processing lengthy request | WebDAV |
| 103 | Early Hints | Preload resources while preparing response | Link headers |

## 2xx Success Responses

| Code | Name | Description | Common Usage |
|------|------|-------------|--------------|
| 200 | OK | Standard successful response | GET, POST success |
| 201 | Created | Resource successfully created | POST/PUT creating resource |
| 202 | Accepted | Request accepted for processing | Async operations |
| 203 | Non-Authoritative Information | Modified response from proxy | Proxy transformations |
| 204 | No Content | Success with no response body | DELETE operations |
| 205 | Reset Content | Client should reset document view | Form reset |
| 206 | Partial Content | Partial resource returned | Range requests, video streaming |
| 207 | Multi-Status | Multiple status values | WebDAV |
| 208 | Already Reported | Members already enumerated | WebDAV |
| 226 | IM Used | Instance manipulations applied | Delta encoding |

## 3xx Redirection Responses

| Code | Name | Description | SEO Impact | Caching |
|------|------|-------------|------------|---------|
| 300 | Multiple Choices | Multiple options available | Neutral | Cacheable |
| 301 | Moved Permanently | Resource permanently moved | Passes link equity | Cacheable |
| 302 | Found | Resource temporarily moved | No link equity | Not cached |
| 303 | See Other | Redirect to different resource | N/A | Never cached |
| 304 | Not Modified | Resource unchanged since last request | N/A | Updates cache |
| 305 | Use Proxy | Must use specified proxy | Deprecated | N/A |
| 307 | Temporary Redirect | Temporary redirect, maintain method | No link equity | Not cached |
| 308 | Permanent Redirect | Permanent redirect, maintain method | Passes link equity | Cacheable |

## 4xx Client Error Responses

| Code | Name | Description | Common Causes |
|------|------|-------------|---------------|
| 400 | Bad Request | Invalid request syntax | Malformed request, invalid JSON |
| 401 | Unauthorized | Authentication required | Missing/invalid credentials |
| 402 | Payment Required | Reserved for future use | Digital payment systems |
| 403 | Forbidden | Server refuses to authorize | Insufficient permissions |
| 404 | Not Found | Resource not found | Wrong URL, deleted resource |
| 405 | Method Not Allowed | HTTP method not supported | POST to read-only resource |
| 406 | Not Acceptable | Content negotiation failed | Accept header mismatch |
| 407 | Proxy Authentication Required | Proxy authentication needed | Corporate proxies |
| 408 | Request Timeout | Request took too long | Slow client, network issues |
| 409 | Conflict | Request conflicts with server state | Version conflicts, duplicate resources |
| 410 | Gone | Resource permanently deleted | Intentionally removed content |
| 411 | Length Required | Content-Length header missing | POST/PUT without length |
| 412 | Precondition Failed | Precondition headers failed | If-Match failure |
| 413 | Payload Too Large | Request body too large | File upload limits |
| 414 | URI Too Long | URI exceeds server limits | GET with huge parameters |
| 415 | Unsupported Media Type | Media type not supported | Wrong Content-Type |
| 416 | Range Not Satisfiable | Range header invalid | Invalid byte range |
| 417 | Expectation Failed | Expect header requirements failed | 100-continue failure |
| 418 | I'm a teapot | April Fools joke (RFC 2324) | Never (joke status) |
| 421 | Misdirected Request | Request sent to wrong server | HTTP/2 connection reuse |
| 422 | Unprocessable Entity | Request understood but invalid | Validation errors |
| 423 | Locked | Resource is locked | WebDAV locked resources |
| 424 | Failed Dependency | Previous request failed | WebDAV dependencies |
| 425 | Too Early | Server unwilling to risk replay | 0-RTT data |
| 426 | Upgrade Required | Client should switch protocols | Force HTTP/2 |
| 428 | Precondition Required | Request must be conditional | Prevent lost updates |
| 429 | Too Many Requests | Rate limiting triggered | API throttling |
| 431 | Request Header Fields Too Large | Headers exceed limits | Cookie bombs |
| 451 | Unavailable For Legal Reasons | Censored content | Legal compliance |

## 5xx Server Error Responses

| Code | Name | Description | Common Causes |
|------|------|-------------|---------------|
| 500 | Internal Server Error | Generic server error | Unhandled exceptions, bugs |
| 501 | Not Implemented | Feature not supported | Unsupported HTTP method |
| 502 | Bad Gateway | Invalid response from upstream | Proxy/gateway issues |
| 503 | Service Unavailable | Server temporarily unavailable | Maintenance, overload |
| 504 | Gateway Timeout | Upstream server timeout | Slow backend services |
| 505 | HTTP Version Not Supported | HTTP version not supported | Ancient clients |
| 506 | Variant Also Negotiates | Content negotiation error | Configuration error |
| 507 | Insufficient Storage | Server storage full | WebDAV storage limits |
| 508 | Loop Detected | Infinite loop detected | WebDAV circular reference |
| 510 | Not Extended | Extensions required | Missing extensions |
| 511 | Network Authentication Required | Network auth needed | Captive portals, Wi-Fi login |

## Common Response Patterns

### API Design Patterns
```
GET /resource/123
  200 OK - Resource found
  404 Not Found - Resource doesn't exist

POST /resource
  201 Created - New resource created
  400 Bad Request - Validation failed
  409 Conflict - Duplicate resource

PUT /resource/123
  200 OK - Resource updated
  201 Created - Resource created
  404 Not Found - Resource doesn't exist

DELETE /resource/123
  204 No Content - Successfully deleted
  404 Not Found - Resource doesn't exist
```

### Authentication Flow
```
No credentials → 401 Unauthorized
Invalid credentials → 401 Unauthorized
Valid credentials, no permission → 403 Forbidden
Valid credentials, has permission → 200 OK
```

### Rate Limiting Headers
```
429 Too Many Requests
Headers:
  Retry-After: 3600
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1620000000
```

## Status Code Best Practices

### When to Use Each Code

| Scenario | Correct Code | Incorrect Code |
|----------|--------------|----------------|
| Resource not found | 404 | 200 with error message |
| No permission | 403 | 401 |
| Not logged in | 401 | 403 |
| Validation error | 400 or 422 | 500 |
| Resource deleted | 204 or 404 | 200 |
| Rate limited | 429 | 503 |
| Maintenance mode | 503 | 500 |

### REST API Conventions

| Method | Success | Created | No Content | Not Found | Conflict |
|--------|---------|---------|------------|-----------|----------|
| GET | 200 | - | - | 404 | - |
| POST | 200/201 | 201 | - | - | 409 |
| PUT | 200 | 201 | 204 | 404 | 409 |
| PATCH | 200 | - | 204 | 404 | 409 |
| DELETE | 200 | - | 204 | 404 | - |

## Debugging Status Codes

### Browser Developer Tools
```javascript
// Check status in browser console
fetch('/api/resource')
  .then(response => {
    console.log('Status:', response.status);
    console.log('Status Text:', response.statusText);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  });
```

### cURL Commands
```bash
# Get status code only
curl -s -o /dev/null -w "%{http_code}" https://example.com

# Verbose output with headers
curl -I https://example.com

# Follow redirects and show all status codes
curl -IL https://example.com
```

### Common Issues and Solutions

| Status | Common Issue | Solution |
|--------|--------------|----------|
| 301/302 Loop | Redirect loop | Check redirect rules |
| 403 on files | File permissions | Check server permissions |
| 404 on API | Wrong endpoint | Verify API documentation |
| 500 intermittent | Memory/resource limits | Check server logs |
| 502 occasional | Backend timeout | Increase timeout, optimize |
| 503 scheduled | Maintenance mode | Implement proper maintenance page |