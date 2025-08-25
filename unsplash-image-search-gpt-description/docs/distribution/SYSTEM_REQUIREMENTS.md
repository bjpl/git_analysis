# System Requirements

Detailed system requirements and compatibility information for the Unsplash Image Search with GPT application.

## Table of Contents

- [Minimum Requirements](#minimum-requirements)
- [Recommended Specifications](#recommended-specifications)
- [Platform Support](#platform-support)
- [Hardware Requirements](#hardware-requirements)
- [Software Dependencies](#software-dependencies)
- [Network Requirements](#network-requirements)
- [Storage Requirements](#storage-requirements)
- [Performance Guidelines](#performance-guidelines)
- [Compatibility Notes](#compatibility-notes)

## Minimum Requirements

### Operating System
- **Windows**: Windows 10 (1903) or later
- **macOS**: macOS 10.14 (Mojave) or later
- **Linux**: Ubuntu 18.04 LTS or equivalent

### Hardware
- **Processor**: x86-64 compatible CPU (Intel/AMD)
- **Memory**: 4 GB RAM
- **Storage**: 500 MB free disk space
- **Display**: 1024x768 minimum resolution
- **Network**: Internet connection required

### Software
- **Python**: 3.8+ (for source installations)
- **Internet Browser**: For API key setup
- **Graphics**: Basic GPU with DirectX 9/OpenGL 2.1

## Recommended Specifications

### For Optimal Performance
- **Operating System**: Latest stable version
- **Processor**: Multi-core CPU (4+ cores, 2.0 GHz+)
- **Memory**: 8 GB RAM or more
- **Storage**: 2 GB free space (1 GB for cache)
- **Display**: 1920x1080 or higher
- **Network**: Broadband (5+ Mbps) for smooth image loading

### For Heavy Usage
- **Memory**: 16 GB RAM
- **Storage**: SSD with 5+ GB free space
- **Network**: High-speed broadband (25+ Mbps)
- **Display**: Large monitor (24"+) for better vocabulary viewing

## Platform Support

### Windows Support

#### Fully Supported (Pre-built Executables)
- ✅ **Windows 10** (version 1903+)
- ✅ **Windows 11** (all versions)

#### Limited Support (Source Installation Only)
- ⚠️ **Windows 8.1** (with updates)
- ⚠️ **Windows Server 2019/2022**

#### Not Supported
- ❌ Windows 7 and earlier
- ❌ Windows RT/ARM versions

### macOS Support

#### Supported Versions
- ✅ **macOS 14 (Sonoma)** - Latest
- ✅ **macOS 13 (Ventura)** - Full support
- ✅ **macOS 12 (Monterey)** - Full support
- ✅ **macOS 11 (Big Sur)** - Full support
- ⚠️ **macOS 10.15 (Catalina)** - Source only
- ⚠️ **macOS 10.14 (Mojave)** - Source only

#### Architecture Support
- ✅ **Apple Silicon (M1/M2/M3)** - Native support
- ✅ **Intel x86-64** - Native support

### Linux Support

#### Tested Distributions
- ✅ **Ubuntu**: 20.04 LTS, 22.04 LTS, 23.10
- ✅ **Debian**: 10 (Buster), 11 (Bullseye), 12 (Bookworm)
- ✅ **CentOS/RHEL**: 8, 9
- ✅ **Fedora**: 36, 37, 38
- ✅ **Arch Linux**: Rolling release
- ⚠️ **openSUSE**: Leap 15.4+

#### Desktop Environments
- ✅ **GNOME** (3.36+, 40+)
- ✅ **KDE Plasma** (5.18+)
- ✅ **XFCE** (4.14+)
- ⚠️ **Unity**, **MATE**, **Cinnamon** (basic support)

## Hardware Requirements

### Processor (CPU)

#### Minimum
- **Architecture**: x86-64 (64-bit)
- **Speed**: 1.5 GHz single-core
- **Examples**: Intel Core i3-4xxx, AMD A8-series

#### Recommended
- **Cores**: 4+ cores
- **Speed**: 2.0 GHz+
- **Examples**: Intel Core i5-8xxx+, AMD Ryzen 5+
- **Features**: SSE4.2, AVX for image processing

#### Performance Notes
- **Image processing**: Benefits from multiple cores
- **AI descriptions**: Single-threaded (network-bound)
- **UI responsiveness**: Needs adequate single-core performance

### Memory (RAM)

#### Minimum: 4 GB
- **Application**: ~100-200 MB
- **Python runtime**: ~50-100 MB
- **Image cache**: ~100-500 MB
- **System overhead**: ~3 GB

#### Recommended: 8 GB+
- **Smooth operation**: Multiple images cached
- **Large images**: High-resolution image handling
- **Multitasking**: Run alongside other applications

#### Memory Usage Patterns
```
Typical Session Memory Usage:
┏━━━━━━━━━━━━━━━━━━┓
┃ Component    | Memory ┃
┣━━━━━━━━━━━━━━━━━━┫
┃ App Core     | 80 MB  ┃
┃ UI Framework | 50 MB  ┃
┃ Image Cache  | 200 MB ┃
┃ Session Data | 20 MB  ┃
┃ Temp Files   | 50 MB  ┃
┗━━━━━━━━━━━━━━━━━━┛
```

### Storage

#### Minimum: 500 MB
- **Application**: 50-100 MB (executable)
- **Dependencies**: 100-200 MB (if source install)
- **User data**: 50-100 MB
- **Cache**: 100-200 MB
- **System temp**: 50-100 MB

#### Recommended: 2+ GB
- **Large cache**: 1 GB for image caching
- **Session history**: Extended session logging
- **Vocabulary exports**: Multiple export formats
- **Updates**: Space for application updates

#### Storage Types
- **SSD**: Recommended for cache performance
- **HDD**: Acceptable for basic usage
- **Network drives**: Not recommended for cache

### Display

#### Minimum Resolution: 1024x768
- **UI scaling**: Interface fits at minimum size
- **Image viewing**: Basic image display
- **Vocabulary panels**: Limited space for word lists

#### Recommended: 1920x1080+
- **Optimal layout**: All UI elements clearly visible
- **Image quality**: Full image detail display
- **Productivity**: Side-by-side panels work well

#### High-DPI Support
- **Windows**: Automatic scaling (100%, 125%, 150%)
- **macOS**: Retina display support
- **Linux**: Manual scaling may be needed

## Software Dependencies

### Python Environment (Source Installations)

#### Core Dependencies
```txt
Python >= 3.8.0
tkinter (GUI framework) - Usually included
PIL/Pillow >= 8.0.0 (image processing)
requests >= 2.25.0 (HTTP client)
openai >= 1.0.0 (API client)
python-dotenv >= 0.19.0 (configuration)
```

#### System Libraries

**Windows**:
- Visual C++ Redistributable 2019+
- Windows API libraries (included)

**macOS**:
- Xcode Command Line Tools (for source builds)
- Tcl/Tk 8.6+ (usually included)

**Linux**:
```bash
# Ubuntu/Debian
apt install python3-tk python3-pil python3-dev

# CentOS/RHEL
yum install tkinter python3-pillow python3-devel

# Arch Linux
pacman -S tk python-pillow
```

### Runtime Requirements

#### Graphics Support
- **2D graphics**: Basic raster operations
- **Image formats**: JPEG, PNG, WebP support
- **Color depth**: 24-bit color minimum
- **Hardware acceleration**: Not required but helpful

#### Font Support
- **System fonts**: Default UI fonts
- **Unicode**: Full Unicode text support
- **International**: Multi-language character display

## Network Requirements

### Internet Connection

#### Required
- **Type**: Broadband internet connection
- **Stability**: Consistent connection for API calls
- **Protocols**: HTTPS (port 443) access

#### Speed Recommendations

**Minimum (1 Mbps)**:
- Basic functionality works
- Slower image loading (5-10 seconds)
- Description generation may timeout

**Recommended (5+ Mbps)**:
- Smooth image loading (2-5 seconds)
- Reliable API operations
- Good overall experience

**Optimal (25+ Mbps)**:
- Instant image loading
- Multiple simultaneous operations
- No timeout issues

### Network Configuration

#### Required Access
- **Unsplash API**: `api.unsplash.com` (HTTPS)
- **Unsplash Images**: `images.unsplash.com` (HTTPS)
- **OpenAI API**: `api.openai.com` (HTTPS)

#### Firewall Requirements
- **Outbound HTTPS** (port 443) to above domains
- **DNS resolution** for API endpoints
- **No proxy authentication** (or configured proxy)

#### Corporate Networks
- May require IT approval for API access
- Proxy configuration might be needed
- SSL inspection can cause certificate issues

### Data Usage

#### Typical Usage
```
Per Session Estimates:
┏━━━━━━━━━━━━━━━━━━━━━┓
┃ Activity      | Data Used ┃
┣━━━━━━━━━━━━━━━━━━━━━┫
┃ Image search  | 100-500 KB ┃
┃ Image load    | 500 KB-2 MB┃
┃ AI description| 5-20 KB    ┃
┃ Translation   | 1-5 KB     ┃
┗━━━━━━━━━━━━━━━━━━━━━┛

20 images = ~10-40 MB data
```

## Storage Requirements

### Installation Size

#### Windows Installer
- **Download**: 50-70 MB
- **Installed**: 80-120 MB
- **With examples**: +20 MB

#### Portable Version
- **Download**: 40-60 MB (ZIP)
- **Extracted**: 50-80 MB

#### Source Installation
- **Repository**: 10-20 MB
- **Dependencies**: 100-300 MB (pip install)
- **Cache**: 50-200 MB (pip cache)

### Runtime Storage

#### User Data Growth
```
Estimated Growth (per month):
┏━━━━━━━━━━━━━━━━━━━━━┓
┃ Usage Level | Storage    ┃
┣━━━━━━━━━━━━━━━━━━━━━┫
┃ Light       | 10-50 MB   ┃
┃ Moderate    | 50-200 MB  ┃
┃ Heavy       | 200-500 MB ┃
┗━━━━━━━━━━━━━━━━━━━━━┛
```

#### File Types and Sizes
- **Vocabulary CSV**: 1-10 MB (1,000s of entries)
- **Session logs**: 1-50 MB (detailed history)
- **Image cache**: 100-1000 MB (cached images)
- **Exports**: 1-20 MB (various formats)
- **Config files**: <1 MB

### Storage Management

#### Automatic Cleanup
- **Image cache**: LRU eviction (configurable size)
- **Temp files**: Cleaned on startup
- **Old logs**: Manual cleanup required

#### Manual Cleanup
```bash
# Clear image cache
rm -rf data/cache/*

# Archive old sessions
mv session_log.json session_log_backup.json

# Clean old exports
rm data/exports/*.txt
```

## Performance Guidelines

### Expected Performance

#### Image Search
- **Search API call**: 0.5-2 seconds
- **Image download**: 1-5 seconds (varies by size/speed)
- **Image display**: <1 second
- **Cache hit**: <0.5 seconds

#### Description Generation
- **gpt-4o-mini**: 3-15 seconds
- **gpt-4o**: 8-30 seconds
- **Phrase extraction**: 5-20 seconds
- **Network dependent**: Varies by connection

#### UI Responsiveness
- **Startup time**: 2-5 seconds
- **Search input**: Instant
- **Button clicks**: <0.5 seconds
- **Theme switching**: 1-2 seconds

### Performance Optimization

#### For Slower Systems
1. **Reduce cache size**: Limit memory usage
2. **Lower image zoom**: Reduce processing load
3. **Close other apps**: Free up resources
4. **Use SSD**: Faster file operations

#### For Better Networks
1. **Increase cache size**: More images cached
2. **Enable prefetching**: Download next images
3. **Batch operations**: Multiple API calls

### Performance Monitoring

#### Built-in Statistics
- Session statistics (images viewed, words learned)
- API response times (visible in status bar)
- Memory usage indicators

#### External Monitoring
```bash
# Monitor system resources
top -p $(pgrep -f unsplash)    # Linux/Mac
# Task Manager on Windows

# Network monitoring
netstat -an | grep :443        # Check HTTPS connections
```

## Compatibility Notes

### Known Issues

#### Windows
- **High DPI**: Some UI elements may be small on high-DPI displays
- **Windows Defender**: May quarantine executable on first run
- **Corporate networks**: Proxy authentication issues

#### macOS
- **Gatekeeper**: Unsigned app warning on first launch
- **Python versions**: System vs Homebrew Python conflicts
- **M1/M2 Macs**: Rosetta translation for Intel Python

#### Linux
- **Wayland**: Some display issues on Wayland sessions
- **Font rendering**: May look different across distributions
- **X11 forwarding**: Limited support for remote X sessions

### Workarounds

#### Display Issues
1. **Scaling problems**: Set environment variables
   ```bash
   export GDK_SCALE=1.5
   export GDK_DPI_SCALE=0.5
   ```

2. **Font issues**: Install additional font packages
   ```bash
   sudo apt install fonts-dejavu-core fonts-liberation
   ```

#### Network Issues
1. **Corporate proxy**: Configure proxy settings
   ```bash
   export https_proxy=http://proxy:8080
   ```

2. **SSL issues**: Update certificates
   ```bash
   sudo apt update && sudo apt install ca-certificates
   ```

### Future Compatibility

#### Planned Improvements
- **ARM64 support**: Native Windows ARM builds
- **Wayland**: Better Linux display server support
- **Container**: Docker/Flatpak distribution options
- **PWA version**: Browser-based version

#### API Evolution
- **Unsplash**: Following API v2 development
- **OpenAI**: Supporting newer GPT models
- **Backward compatibility**: Maintaining config format compatibility

---

## Compatibility Matrix

### Quick Reference

| Platform | Version | Status | Installation Method |
|----------|---------|--------|-----------------|
| Windows 10 | 1903+ | ✅ Full | Installer/Portable |
| Windows 11 | All | ✅ Full | Installer/Portable |
| macOS | 11+ | ✅ Full | Source/App Bundle |
| macOS | 10.14-10.15 | ⚠️ Limited | Source Only |
| Ubuntu | 20.04+ | ✅ Full | Source/AppImage |
| Debian | 11+ | ✅ Full | Source/Package |
| CentOS/RHEL | 8+ | ✅ Full | Source |
| Arch Linux | Current | ✅ Full | Source/AUR |

### Legend
- ✅ **Full**: Complete feature support with pre-built binaries
- ⚠️ **Limited**: Core features work, may need source installation
- ❌ **Not Supported**: Does not work or not tested

---

**Questions about compatibility?** Check our [GitHub Issues](https://github.com/your-username/unsplash-image-search-gpt-description/issues) or create a new issue with your system specifications.