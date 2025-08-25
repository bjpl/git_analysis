# Known Issues and Limitations

This document tracks known issues, limitations, and workarounds for the Unsplash Image Search with GPT application.

## Table of Contents

- [Current Known Issues](#current-known-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [API-Related Issues](#api-related-issues)
- [Performance Limitations](#performance-limitations)
- [UI/UX Issues](#uiux-issues)
- [Compatibility Issues](#compatibility-issues)
- [Workarounds](#workarounds)
- [Planned Fixes](#planned-fixes)
- [Reporting New Issues](#reporting-new-issues)

## Current Known Issues

### Critical Issues (Priority: High)

#### Memory Usage with Large Images
**Issue ID**: #001  
**Status**: 🔴 Open  
**Affects**: All platforms  
**Description**: Application uses excessive memory (>1GB) when processing very large images (>10MB)  

**Symptoms**:
- Application becomes unresponsive
- System memory consumption spikes
- Potential crash on systems with <8GB RAM

**Workaround**:
```
1. Avoid zooming beyond 200% on large images
2. Clear image cache regularly (data/cache/)
3. Restart application after processing 20+ images
```

**Root Cause**: PIL image processing creates multiple copies in memory  
**Target Fix**: v2.1.0

---

#### Occasional UI Freeze on Theme Switch (macOS)
**Issue ID**: #002  
**Status**: 🔴 Open  
**Affects**: macOS 13+  
**Description**: Application becomes temporarily unresponsive when switching between light/dark themes  

**Symptoms**:
- 2-5 second freeze when pressing Ctrl+T
- UI elements may flicker
- Application recovers automatically

**Workaround**:
```
1. Wait for theme switch to complete
2. Avoid rapid theme switching
3. Restart app if freeze persists >10 seconds
```

**Root Cause**: Tkinter theme system conflicts with macOS appearance changes  
**Target Fix**: v2.0.1

---

### High Priority Issues

#### Export to Anki Requires Manual Import Setup
**Issue ID**: #003  
**Status**: 🟡 Acknowledged  
**Affects**: All platforms  
**Description**: Exported Anki files need manual configuration in Anki for proper formatting  

**Symptoms**:
- Anki import shows formatting issues
- Cards don't display context properly
- Manual field mapping required

**Workaround**:
```
Anki Import Settings:
1. Field separator: Tab
2. Field 1: Front (Spanish)
3. Field 2: Back (English + Context)
4. Allow HTML in fields: Yes
```

**Root Cause**: Anki export format needs better field definitions  
**Target Fix**: v2.1.0

---

#### High DPI Display Scaling Issues
**Issue ID**: #004  
**Status**: 🟡 Acknowledged  
**Affects**: Windows 10/11 with >125% scaling  
**Description**: UI elements appear too small or misaligned on high-DPI displays  

**Symptoms**:
- Small text and buttons
- Misaligned interface elements
- Blurry icons and images

**Workaround**:
```
Windows:
1. Right-click executable → Properties
2. Compatibility tab → "Change high DPI settings"
3. Check "Override high DPI scaling"
4. Select "System" from dropdown
```

**Root Cause**: Tkinter DPI awareness needs improvement  
**Target Fix**: v2.2.0

---

### Medium Priority Issues

#### Slow Image Loading on Slow Connections
**Issue ID**: #005  
**Status**: 🟡 Acknowledged  
**Affects**: All platforms  
**Description**: Images take 10+ seconds to load on connections <1 Mbps  

**Symptoms**:
- Long delays before image appears
- No progress indicator during download
- Possible timeout errors

**Workaround**:
```
1. Use faster internet connection
2. Wait patiently for images to load
3. Try different search terms if timeout occurs
```

**Enhancement Plan**: Add image size options and progress indicators  
**Target Fix**: v2.1.0

---

#### Configuration File Corruption on Abnormal Exit
**Issue ID**: #006  
**Status**: 🟡 Acknowledged  
**Affects**: All platforms  
**Description**: Config.ini becomes corrupted if application crashes during write operation  

**Symptoms**:
- Application won't start after crash
- "Configuration error" message
- Lost API key settings

**Workaround**:
```
1. Delete config.ini file
2. Restart application
3. Re-enter API keys in setup wizard
```

**Root Cause**: No atomic write operations for config file  
**Target Fix**: v2.0.1

---

## Platform-Specific Issues

### Windows Issues

#### Windows Defender False Positive
**Issue ID**: #W001  
**Status**: 🟡 Acknowledged  
**Affects**: Windows 10/11 with Windows Defender  
**Description**: Executable may be flagged as potentially unwanted software  

**Symptoms**:
- Download blocked by browser
- File quarantined by Windows Defender
- SmartScreen warning on first run

**Workaround**:
```
1. Click "More info" on SmartScreen warning
2. Click "Run anyway"
3. Add to Windows Defender exclusions if needed
```

**Root Cause**: Unsigned executable triggers security warnings  
**Target Fix**: Code signing in v2.1.0

---

#### Path Length Limitations
**Issue ID**: #W002  
**Status**: 🟠 Low Priority  
**Affects**: Windows (all versions)  
**Description**: Issues with very long file paths (>260 characters)  

**Symptoms**:
- Export fails with "path too long" error
- Cache files not created in deep directory structures

**Workaround**:
```
1. Install to shorter path (e.g., C:\UnsplashGPT)
2. Use shorter data directory names
3. Enable long path support in Windows 10+
```

**Root Cause**: Python path handling limitations  
**Target Fix**: v2.2.0

---

### macOS Issues

#### Gatekeeper Quarantine Warning
**Issue ID**: #M001  
**Status**: 🟡 Acknowledged  
**Affects**: macOS 10.15+  
**Description**: Application blocked on first run due to lack of code signing  

**Symptoms**:
- "App can't be opened" dialog
- Developer verification warning
- Application won't launch

**Workaround**:
```
1. Right-click app → Open
2. Click "Open" in security dialog
3. Or: System Preferences → Security → "Open Anyway"
```

**Root Cause**: Application not notarized by Apple  
**Target Fix**: Code signing and notarization in v2.1.0

---

#### Python Version Conflicts
**Issue ID**: #M002  
**Status**: 🟠 Low Priority  
**Affects**: macOS (source installations)  
**Description**: Conflicts between system Python, Homebrew Python, and pyenv  

**Symptoms**:
- ImportError for tkinter
- Missing dependencies
- Application won't start

**Workaround**:
```
1. Use system Python: /usr/bin/python3
2. Or create isolated virtual environment
3. Install with specific Python version
```

**Root Cause**: Multiple Python installations  
**Target Fix**: Better installation documentation v2.0.1

---

### Linux Issues

#### Wayland Display Server Issues
**Issue ID**: #L001  
**Status**: 🟡 Acknowledged  
**Affects**: Ubuntu 22.04+, Fedora 36+ (Wayland)  
**Description**: UI rendering issues on Wayland display server  

**Symptoms**:
- Blurry or pixelated interface
- Window positioning problems
- Keyboard shortcuts not working

**Workaround**:
```
1. Switch to X11 session at login
2. Or set environment variables:
   export GDK_BACKEND=x11
   export QT_QPA_PLATFORM=xcb
3. Run application from X11 session
```

**Root Cause**: Tkinter limited Wayland support  
**Target Fix**: v2.2.0 (investigate alternative GUI frameworks)

---

#### Missing System Dependencies
**Issue ID**: #L002  
**Status**: 🟠 Low Priority  
**Affects**: Minimal Linux installations  
**Description**: Missing python3-tk or other system packages  

**Symptoms**:
- "No module named 'tkinter'" error
- Import errors for PIL
- Application crashes on startup

**Workaround**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk python3-pil python3-pil.imagetk

# CentOS/RHEL
sudo yum install tkinter python3-pillow

# Arch Linux
sudo pacman -S tk python-pillow
```

**Root Cause**: System dependencies not automatically installed  
**Target Fix**: Better dependency documentation v2.0.1

---

## API-Related Issues

### Unsplash API Issues

#### Rate Limit Exceeded
**Issue ID**: #A001  
**Status**: 🟡 By Design  
**Affects**: All users  
**Description**: Free tier limited to 50 requests per hour  

**Symptoms**:
- "Rate limit exceeded" error
- No new images load
- Error persists for up to 1 hour

**Workaround**:
```
1. Wait for hourly rate limit reset
2. Apply for Production access (5,000/hour)
3. Monitor usage in application stats
```

**Root Cause**: Unsplash API free tier limitations  
**Enhancement**: Add rate limit monitoring in v2.1.0

---

#### Image URL Expiration
**Issue ID**: #A002  
**Status**: 🟠 Low Priority  
**Affects**: All users  
**Description**: Cached image URLs expire after 24-48 hours  

**Symptoms**:
- Cached images fail to load
- "Image not found" errors
- Need to search again for same images

**Workaround**:
```
1. Clear image cache periodically
2. Re-search for images if errors occur
3. Download images immediately if needed long-term
```

**Root Cause**: Unsplash CDN URL expiration policy  
**Enhancement**: Implement image download/storage option v2.2.0

---

### OpenAI API Issues

#### Inconsistent Description Quality
**Issue ID**: #A003  
**Status**: 🟡 By Design  
**Affects**: All users  
**Description**: Description quality varies significantly between images  

**Symptoms**:
- Very short or generic descriptions
- Hallucinated details not in image
- Inconsistent Spanish language quality

**Workaround**:
```
1. Add specific context notes
2. Try regenerating description
3. Use gpt-4o for better quality (higher cost)
```

**Root Cause**: AI model limitations and variability  
**Enhancement**: Improve prompting strategy v2.1.0

---

#### Token Limit Exceeded
**Issue ID**: #A004  
**Status**: 🟠 Low Priority  
**Affects**: Users with very long notes  
**Description**: Very long user notes cause token limit errors  

**Symptoms**:
- "Token limit exceeded" error
- Description generation fails
- No error recovery

**Workaround**:
```
1. Keep user notes under 500 words
2. Break long descriptions into segments
3. Remove excessive detail from notes
```

**Root Cause**: OpenAI API token limits  
**Target Fix**: Add input validation and truncation v2.0.1

---

## Performance Limitations

### Memory Usage

#### Image Cache Memory Growth
**Issue ID**: #P001  
**Status**: 🟡 Acknowledged  
**Affects**: Extended usage sessions  
**Description**: Memory usage grows continuously during extended use  

**Symptoms**:
- RAM usage increases over time
- System becomes sluggish
- Eventual application crash

**Current Mitigation**:
- LRU cache with size limits
- Automatic cleanup on startup

**Workaround**:
```
1. Restart application every 50-100 images
2. Clear cache manually: delete data/cache/*
3. Reduce zoom levels to minimize memory usage
```

**Target Fix**: Improved memory management v2.1.0

---

#### Startup Time on Slow Systems
**Issue ID**: #P002  
**Status**: 🟠 Low Priority  
**Affects**: Systems with HDD, <4GB RAM  
**Description**: Application takes >30 seconds to start on slow systems  

**Symptoms**:
- Long delay before UI appears
- High disk activity during startup
- Sluggish initial response

**Workaround**:
```
1. Install on SSD if possible
2. Close other applications during startup
3. Be patient during first launch
```

**Root Cause**: Large executable size and dependency loading  
**Enhancement**: Optimize startup process v2.2.0

---

### Network Performance

#### Concurrent API Calls
**Issue ID**: #P003  
**Status**: 🟠 Enhancement  
**Affects**: All users  
**Description**: API calls are sequential, slowing down workflow  

**Symptoms**:
- Must wait for description before searching next image
- No background processing
- Inefficient for batch operations

**Current Limitation**: Single-threaded API operations  

**Enhancement Plan**: Implement concurrent processing v2.2.0

---

## UI/UX Issues

### Interface Limitations

#### No Undo Functionality
**Issue ID**: #U001  
**Status**: 🟠 Enhancement  
**Affects**: All users  
**Description**: No way to undo actions like clearing text or deleting vocabulary  

**Symptoms**:
- Accidental data loss
- Need to retype information
- No recovery options

**Workaround**:
```
1. Copy important text before clearing
2. Regular vocabulary exports as backup
3. Be careful with destructive operations
```

**Enhancement Plan**: Add undo/redo functionality v2.3.0

---

#### Limited Keyboard Navigation
**Issue ID**: #U002  
**Status**: 🟡 Partially Addressed  
**Affects**: Accessibility users  
**Description**: Some UI elements not accessible via keyboard  

**Symptoms**:
- Tab navigation skips some buttons
- Extracted phrases not keyboard accessible
- No keyboard shortcuts for all functions

**Current Status**: Basic shortcuts implemented in v2.0.0  

**Enhancement Plan**: Complete keyboard navigation v2.1.0

---

#### Window Resizing Issues
**Issue ID**: #U003  
**Status**: 🟡 Acknowledged  
**Affects**: Small screens, mobile devices  
**Description**: Interface doesn't adapt well to small screen sizes  

**Symptoms**:
- UI elements overlap on small screens
- Minimum window size too large
- Poor responsiveness

**Workaround**:
```
1. Use minimum resolution of 1024x768
2. Maximize window for best experience
3. Use external monitor if available
```

**Target Fix**: Responsive design improvements v2.2.0

---

## Compatibility Issues

### Operating System Compatibility

#### Windows 7 Support Dropped
**Issue ID**: #C001  
**Status**: 🔴 Won't Fix  
**Affects**: Windows 7 users  
**Description**: Application no longer supports Windows 7  

**Reason**: Python 3.8+ requirement, security considerations  

**Alternative**: Use legacy version v1.5.2 or upgrade to Windows 10+

---

#### Python Version Requirements
**Issue ID**: #C002  
**Status**: 🟡 By Design  
**Affects**: Python <3.8 users  
**Description**: Application requires Python 3.8 or newer  

**Symptoms**:
- Syntax errors on startup
- Import failures
- Dependency conflicts

**Solution**: Upgrade to Python 3.8+ or use pre-built executable

---

### Hardware Compatibility

#### ARM64 Support Limited
**Issue ID**: #C003  
**Status**: 🟡 Planned  
**Affects**: ARM-based systems  
**Description**: Limited testing and optimization for ARM processors  

**Current Status**: 
- Windows ARM: Not tested
- macOS Apple Silicon: Partially supported
- Linux ARM: Community supported

**Target**: Full ARM64 support v2.2.0

---

## Workarounds

### General Performance Improvements

```bash
# Clear caches regularly
rm -rf data/cache/*
rm -rf __pycache__/*

# Optimize system for better performance
# Close unnecessary applications
# Use SSD storage when possible
# Ensure adequate RAM (8GB+ recommended)
```

### Configuration Optimizations

```ini
# config.ini optimizations
[SETTINGS]
CACHE_SIZE=50          # Reduce memory usage
ZOOM_LEVEL=100         # Avoid high zoom levels
THEME=system          # Use system theme for better performance
AUTO_SAVE=true        # Prevent data loss
```

### Network Optimization

```bash
# For slow connections
# Use minimal search terms
# Avoid rapid searches
# Wait for operations to complete

# For corporate networks
# Configure proxy settings
# Whitelist required domains:
# - api.unsplash.com
# - images.unsplash.com
# - api.openai.com
```

## Planned Fixes

### Version 2.0.1 (Hotfix - Target: 2024-01-30)
- ✅ Fix configuration file corruption (#006)
- ✅ Add token limit validation (#A004)
- ✅ Improve documentation for Linux dependencies (#L002)
- ✅ macOS theme switching issue (#002)

### Version 2.1.0 (Minor Release - Target: 2024-02-15)
- 🔄 Memory usage optimization (#001)
- 🔄 Enhanced Anki export format (#003)
- 🔄 Rate limit monitoring (#A001)
- 🔄 Improved AI prompting (#A003)
- 🔄 Complete keyboard navigation (#U002)
- 🔄 Code signing for Windows/macOS

### Version 2.2.0 (Minor Release - Target: 2024-03-15)
- 🔄 High DPI support improvements (#004)
- 🔄 Responsive design (#U003)
- 🔄 Concurrent API processing (#P003)
- 🔄 ARM64 optimization (#C003)
- 🔄 Wayland compatibility investigation (#L001)
- 🔄 Image download/storage option (#A002)

### Version 2.3.0 (Minor Release - Target: 2024-04-15)
- 🔄 Undo/Redo functionality (#U001)
- 🔄 Batch processing capabilities
- 🔄 Enhanced startup performance (#P002)
- 🔄 Plugin system architecture

## Reporting New Issues

### Before Reporting

1. **Search existing issues**: Check [GitHub Issues](https://github.com/your-username/unsplash-image-search-gpt-description/issues)
2. **Check this document**: Issue might be already known
3. **Try workarounds**: Test suggested solutions
4. **Update application**: Ensure you're using latest version

### Issue Report Template

```markdown
**Bug Description**
Clear description of the problem

**Environment**
- OS: [Windows 10/11, macOS version, Linux distro]
- Version: [Application version]
- Installation: [Installer, portable, source]
- Python Version: [If applicable]

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots/Logs**
[Attach if applicable]

**Additional Context**
[Any other relevant information]
```

### Issue Priorities

- 🔴 **Critical**: Application crashes, data loss, security issues
- 🟡 **High**: Major features broken, significant usability issues
- 🟠 **Medium**: Minor features affected, workarounds available
- ⚪ **Low**: Cosmetic issues, enhancement requests

### Response Times

- **Critical**: 24-48 hours
- **High**: 3-5 business days
- **Medium**: 1-2 weeks
- **Low**: Best effort, may be included in future releases

---

## Issue Status Legend

- 🔴 **Open**: Confirmed issue, not yet fixed
- 🟡 **Acknowledged**: Issue confirmed, assigned to release
- 🔄 **In Progress**: Being actively worked on
- ✅ **Fixed**: Fixed in latest version
- 🟠 **Enhancement**: Feature request or improvement
- 🔴 **Won't Fix**: Issue will not be addressed

---

**Last Updated**: January 15, 2024  
**Next Review**: February 1, 2024

For the most current issue status, check the [GitHub Issues](https://github.com/your-username/unsplash-image-search-gpt-description/issues) page.