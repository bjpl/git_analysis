# Troubleshooting Guide

This comprehensive troubleshooting guide covers common issues and solutions for the Unsplash Image Search with GPT application.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [API Configuration Problems](#api-configuration-problems)
- [Application Errors](#application-errors)
- [Performance Issues](#performance-issues)
- [Network and Connectivity](#network-and-connectivity)
- [Platform-Specific Issues](#platform-specific-issues)
- [Data and File Issues](#data-and-file-issues)
- [Advanced Troubleshooting](#advanced-troubleshooting)
- [Getting Help](#getting-help)

## Quick Diagnostics

### Self-Diagnostic Checklist

Run through this checklist first:

- [ ] **Internet connection**: Can you browse websites normally?
- [ ] **API keys**: Are they correctly entered without extra spaces?
- [ ] **Account status**: Are your Unsplash/OpenAI accounts active?
- [ ] **Application version**: Are you using the latest release?
- [ ] **System resources**: Do you have enough RAM/storage?
- [ ] **Antivirus**: Is the application being blocked?

### Quick Test Procedure

1. **Launch application**: Does it start without errors?
2. **Search test**: Enter "cat" and search
3. **Image test**: Does an image load?
4. **Description test**: Does "Generar Descripción" work?
5. **Vocabulary test**: Can you click and translate phrases?

If any step fails, jump to the relevant section below.

### Common Error Messages

| Error Message | Quick Fix | Section |
|---------------|-----------|----------|
| "API key not found" | Check config.ini | [API Configuration](#api-configuration-problems) |
| "Rate limit exceeded" | Wait or check usage | [Network Issues](#network-and-connectivity) |
| "Application won't start" | Reinstall or check permissions | [Installation Issues](#installation-issues) |
| "Images not loading" | Check internet/firewall | [Network Issues](#network-and-connectivity) |
| "Description generation failed" | Check OpenAI key/credits | [API Configuration](#api-configuration-problems) |

## Installation Issues

### Application Won't Start

#### Windows Installer Version

**Symptom**: Double-clicking does nothing or shows error

**Solutions**:

1. **Run as Administrator**:
   - Right-click the executable
   - Select "Run as administrator"
   - If it works, there's a permissions issue

2. **Check Windows Defender/Antivirus**:
   - Windows may block unknown executables
   - Add application to antivirus whitelist
   - Temporarily disable real-time protection

3. **Missing Visual C++ Redistributables**:
   ```cmd
   # Download and install from Microsoft:
   # https://aka.ms/vs/17/release/vc_redist.x64.exe
   ```

4. **Corrupted Installation**:
   - Uninstall completely
   - Delete remaining files in installation directory
   - Reinstall fresh copy

#### Portable Version

**Symptom**: Executable doesn't run

**Solutions**:

1. **Extract completely**: Ensure ZIP was fully extracted
2. **Check file integrity**: Re-download if file size doesn't match
3. **Antivirus scanning**: Whitelist the folder
4. **Permissions**: Ensure execute permissions (Linux/Mac)

#### Source Installation

**Symptom**: `python main.py` fails

**Solutions**:

1. **Python version**: Check you have Python 3.8+
   ```bash
   python --version
   # Should show 3.8.0 or higher
   ```

2. **Dependencies missing**:
   ```bash
   pip install -r requirements.txt
   # If fails, try:
   pip install --user -r requirements.txt
   ```

3. **Virtual environment issues**:
   ```bash
   # Create new virtual environment
   python -m venv venv_new
   source venv_new/bin/activate  # Linux/Mac
   # or
   venv_new\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

### Installation Directory Issues

**Problem**: Application installed but can't find files

**Solutions**:

1. **Check installation path**:
   - Default: `C:\Program Files\Unsplash Image Search GPT Description\`
   - Look for `config.ini` and `data` folder

2. **Recreate data directory**:
   ```cmd
   mkdir data
   mkdir data\cache
   mkdir data\exports
   ```

3. **File permissions**:
   - Ensure application can read/write to its directory
   - May need to install to user directory instead

## API Configuration Problems

### "API Key Not Found" Errors

#### Configuration File Issues

**Check config.ini exists**:
```bash
# Should be in application directory
dir config.ini        # Windows
ls -la config.ini      # Linux/Mac
```

**Verify config.ini format**:
```ini
[UNSPLASH]
ACCESS_KEY=your_actual_key_here

[OPENAI]
API_KEY=your_actual_key_here
MODEL=gpt-4o-mini
```

**Common formatting errors**:
- Extra spaces around keys
- Missing section headers `[UNSPLASH]`
- Quotes around keys (don't use quotes)
- Wrong key names (ACCESS_KEY vs API_KEY)

#### Environment Variables Not Loading

**Test environment variables**:
```bash
# Windows
echo %UNSPLASH_ACCESS_KEY%
echo %OPENAI_API_KEY%

# Linux/Mac
echo $UNSPLASH_ACCESS_KEY
echo $OPENAI_API_KEY
```

**Set permanently** (Windows):
1. Search "Environment Variables"
2. Click "Environment Variables" button
3. Add under "User variables"
4. Restart application

### Invalid API Key Errors

#### Unsplash API Key Issues

**Verify key format**:
- Should be 40+ characters long
- Mix of letters and numbers
- No special characters or spaces

**Test manually**:
```bash
curl -H "Authorization: Client-ID YOUR_KEY_HERE" \
  "https://api.unsplash.com/search/photos?query=test&per_page=1"
```

**Common issues**:
- Key copied with extra spaces
- Application status not "Active" in Unsplash dashboard
- Using wrong key (Secret vs Access Key)

#### OpenAI API Key Issues

**Verify key format**:
- Should start with `sk-`
- About 50+ characters long
- Mix of letters, numbers, and sometimes hyphens

**Test manually**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

**Account issues**:
- Payment method not set up
- Account suspended
- Usage limits exceeded
- Insufficient credits

### Rate Limit Issues

#### Unsplash Rate Limits

**Free tier limits**:
- 50 requests per hour
- 5,000 requests per month
- Resets every hour

**Solutions**:
1. **Wait for reset**: Check time until next hour
2. **Monitor usage**: Count searches per hour
3. **Upgrade account**: Apply for Production status
4. **Use efficiently**: Avoid repeated searches

#### OpenAI Rate Limits

**Check usage**:
1. Visit [platform.openai.com/usage](https://platform.openai.com/usage)
2. Check current usage vs limits
3. Verify payment method is active

**Solutions**:
1. **Add credits**: Top up account balance
2. **Increase limits**: Request higher limits if eligible
3. **Wait for reset**: Monthly limits reset on billing date
4. **Use cheaper model**: Switch to gpt-4o-mini

## Application Errors

### UI and Display Issues

#### Images Not Displaying

**Symptom**: Search works but images don't show

**Solutions**:

1. **Check image formats**: Application supports JPG, PNG, WebP
2. **Clear image cache**:
   ```bash
   # Delete cache folder contents
   rm -rf data/cache/*        # Linux/Mac
   del /Q data\cache\*        # Windows
   ```

3. **Network filtering**: Some networks block image downloads
4. **Firewall settings**: Whitelist the application

#### UI Elements Missing or Broken

**Symptom**: Buttons, text fields, or panels missing

**Solutions**:

1. **Window size**: Ensure window is large enough
   - Minimum: 1024x768
   - Recommended: 1200x800+

2. **DPI scaling** (Windows):
   - Right-click executable → Properties
   - Compatibility tab
   - Check "Override high DPI scaling"

3. **Theme issues**: Try switching themes (Ctrl+T)
4. **Reset UI**: Delete config.ini and restart

#### Font or Text Issues

**Symptom**: Text appears garbled or wrong font

**Solutions**:

1. **System fonts**: Install missing system fonts
2. **Encoding issues**: Check system locale settings
3. **Theme conflicts**: Switch to default theme
4. **Restart application**: Sometimes fixes font loading

### Functionality Errors

#### Description Generation Fails

**Symptom**: "Generar Descripción" doesn't work

**Debug steps**:

1. **Check OpenAI status**: [status.openai.com](https://status.openai.com)
2. **Verify model availability**:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_KEY" | grep gpt-4
   ```

3. **Test with simple image**: Try basic photos first
4. **Check account credits**: Visit OpenAI billing page

**Error-specific solutions**:

- **"Model not found"**: Change model to gpt-4o-mini in config
- **"Insufficient quota"**: Add credits to OpenAI account
- **"Invalid request"**: Image might be too large/small

#### Vocabulary Translation Issues

**Symptom**: Clicking phrases doesn't show translations

**Solutions**:

1. **Check phrase extraction**: Ensure description generated first
2. **API key working**: Translation uses same OpenAI key
3. **Network issues**: Check if other API calls work
4. **Clear cache**: Delete temporary files

#### Export Functionality Problems

**Symptom**: Export button doesn't work or creates empty files

**Solutions**:

1. **Check vocabulary data**: Ensure you have words to export
2. **File permissions**: Verify app can write to data directory
3. **Path issues**: Avoid special characters in export path
4. **Disk space**: Ensure sufficient space for export files

## Performance Issues

### Slow Performance

#### Application Startup Slow

**Causes and solutions**:

1. **Large cache**: Clear cache directory
2. **Many sessions**: Archive old session_log.json
3. **Antivirus scanning**: Add to exclusion list
4. **Low memory**: Close other applications

#### Slow Image Loading

**Optimization steps**:

1. **Internet speed**: Test with speedtest.net
2. **Image cache**: Check if cache is working
   ```bash
   ls -la data/cache/  # Should contain image files
   ```
3. **Zoom level**: Lower zoom reduces memory usage
4. **Image size**: Some Unsplash images are very large

#### Slow Description Generation

**Factors affecting speed**:

1. **Model choice**: 
   - gpt-4o-mini: 5-15 seconds
   - gpt-4o: 15-30 seconds

2. **Image complexity**: Simple images process faster
3. **OpenAI server load**: Varies by time of day
4. **Network latency**: Test ping to openai.com

### Memory Issues

#### High Memory Usage

**Symptom**: Application uses >500MB RAM

**Solutions**:

1. **Clear image cache**: Limit cache size in config
2. **Restart periodically**: After 50-100 images
3. **Reduce zoom**: Lower zoom levels use less memory
4. **Close other apps**: Free up system memory

#### Out of Memory Errors

**Symptom**: Application crashes with memory errors

**Solutions**:

1. **Check available RAM**: Ensure 4GB+ free
2. **64-bit version**: Use 64-bit version if available
3. **Virtual memory**: Increase page file size
4. **Image size limits**: Avoid very large images

### Disk Space Issues

**Symptom**: "Disk full" or write errors

**Check disk usage**:
```bash
# Check data directory size
du -sh data/                    # Linux/Mac
dir /s data                     # Windows
```

**Solutions**:
1. **Clear cache**: Delete old cached images
2. **Archive sessions**: Move old session logs
3. **Cleanup exports**: Remove old export files
4. **Move data directory**: Use external drive

## Network and Connectivity

### Connection Timeouts

**Symptom**: "Connection timeout" or "Request failed"

**Network diagnostics**:

1. **Test basic connectivity**:
   ```bash
   ping google.com
   ping api.unsplash.com
   ping api.openai.com
   ```

2. **Check DNS resolution**:
   ```bash
   nslookup api.unsplash.com
   nslookup api.openai.com
   ```

3. **Test HTTPS access**:
   ```bash
   curl -I https://api.unsplash.com
   curl -I https://api.openai.com
   ```

### Firewall and Proxy Issues

#### Corporate Firewalls

**Common restrictions**:
- Blocking API endpoints
- SSL/TLS certificate issues
- Proxy authentication required

**Solutions**:

1. **Whitelist domains**:
   - api.unsplash.com
   - images.unsplash.com
   - api.openai.com

2. **Configure proxy** (if required):
   ```bash
   export https_proxy=http://proxy.company.com:8080
   export http_proxy=http://proxy.company.com:8080
   ```

3. **Contact IT**: Request access to required domains

#### Home Network Issues

**Router/modem problems**:

1. **Restart network equipment**: Unplug for 30 seconds
2. **Update router firmware**: Check manufacturer's website
3. **DNS issues**: Try Google DNS (8.8.8.8, 8.8.4.4)
4. **QoS settings**: Ensure API traffic isn't throttled

### SSL/Certificate Errors

**Symptom**: "Certificate verification failed" or SSL errors

**Solutions**:

1. **Update certificates**: 
   ```bash
   # Windows
   certlm.msc  # Update root certificates
   
   # Linux
   sudo apt update && sudo apt install ca-certificates
   
   # Mac
   # Certificates update automatically
   ```

2. **Check system time**: Incorrect time can cause SSL errors
3. **Corporate certificates**: Install company certificates
4. **Antivirus interference**: Disable SSL/TLS scanning

## Platform-Specific Issues

### Windows Issues

#### Windows Defender Problems

**Symptom**: Application blocked or deleted

**Solutions**:

1. **Add exclusion**:
   - Windows Security → Virus & threat protection
   - Manage settings → Exclusions
   - Add folder or file exclusion

2. **Real-time protection**: Temporarily disable during install
3. **SmartScreen**: Click "More info" → "Run anyway"

#### DLL or Library Issues

**Symptom**: "Missing DLL" or "Library not found"

**Solutions**:

1. **Visual C++ Redistributables**:
   - Download from Microsoft
   - Install both x86 and x64 versions

2. **Windows Updates**: Install all pending updates
3. **System file check**:
   ```cmd
   sfc /scannow
   ```

#### Permission Issues

**Symptom**: "Access denied" when starting

**Solutions**:

1. **Run as administrator**: Right-click → Run as administrator
2. **Install to user directory**: Avoid Program Files
3. **Change ownership**: Take ownership of application folder

### macOS Issues

#### Gatekeeper Blocks Application

**Symptom**: "App can't be opened because it is from an unidentified developer"

**Solutions**:

1. **Override Gatekeeper**:
   - Right-click app → Open
   - Click "Open" in dialog

2. **System Preferences method**:
   - System Preferences → Security & Privacy
   - Click "Open Anyway" button

3. **Command line**:
   ```bash
   sudo xattr -rd com.apple.quarantine /path/to/app
   ```

#### Python/Tkinter Issues

**Symptom**: "No module named tkinter" or GUI doesn't appear

**Solutions**:

1. **Install tkinter**:
   ```bash
   # With Homebrew
   brew install python-tk
   
   # With MacPorts
   sudo port install py311-tkinter
   ```

2. **Use system Python**: `/usr/bin/python3` instead of custom Python
3. **Xcode tools**: `xcode-select --install`

### Linux Issues

#### Missing Dependencies

**Symptom**: "ImportError" or "ModuleNotFoundError"

**Install system dependencies**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk python3-pil python3-pip

# CentOS/RHEL
sudo yum install tkinter python3-pillow python3-pip

# Arch Linux
sudo pacman -S tk python-pillow python-pip
```

#### Display Issues

**Symptom**: GUI appears corrupted or fonts wrong

**Solutions**:

1. **X11 forwarding** (if using SSH):
   ```bash
   ssh -X username@hostname
   export DISPLAY=:0
   ```

2. **Font packages**:
   ```bash
   sudo apt install fonts-dejavu fonts-liberation
   ```

3. **GTK themes**: Install compatible themes

#### Permission Errors

**Symptom**: Can't write to data directory

**Solutions**:

1. **Check permissions**:
   ```bash
   ls -la data/
   chmod 755 data/
   chmod 644 data/*
   ```

2. **User directory**: Run from home directory
3. **Group membership**: Add user to appropriate groups

## Data and File Issues

### Configuration Problems

#### Config File Corruption

**Symptom**: Application won't start or settings lost

**Solutions**:

1. **Backup and recreate**:
   ```bash
   mv config.ini config.ini.backup
   # Run application to create new config
   ```

2. **Manual creation**:
   ```ini
   [UNSPLASH]
   ACCESS_KEY=your_key_here
   
   [OPENAI]
   API_KEY=your_key_here
   MODEL=gpt-4o-mini
   
   [SETTINGS]
   DATA_DIR=data
   THEME=system
   ```

3. **Check file encoding**: Should be UTF-8

#### Data Directory Issues

**Symptom**: "Data directory not found" or permission errors

**Create data structure**:
```bash
mkdir -p data/{cache,exports,sessions}
chmod 755 data data/*
```

**Check disk space**:
```bash
df -h .  # Linux/Mac
dir     # Windows
```

### Vocabulary and Session Data

#### CSV File Corruption

**Symptom**: Vocabulary export fails or shows wrong data

**Recovery steps**:

1. **Check file format**:
   ```bash
   head -5 data/vocabulary.csv
   # Should show: Spanish,English,Date,Search Query,Image URL,Context
   ```

2. **Backup and recreate**:
   ```bash
   cp data/vocabulary.csv data/vocabulary.csv.backup
   # Delete corrupted file, application will recreate
   ```

3. **Manual repair**: Edit in text editor, fix formatting

#### Session Log Issues

**Symptom**: Session history lost or corrupted

**Check session log**:
```bash
# Should be valid JSON
python -m json.tool data/session_log.json
```

**Recovery**:
1. **Backup current**: `cp session_log.json session_log.json.backup`
2. **Reset log**: Delete file, application recreates it
3. **Partial recovery**: Extract data from backup manually

### Cache Problems

#### Cache Size Too Large

**Check cache size**:
```bash
du -sh data/cache/    # Linux/Mac
dir /s data\cache     # Windows
```

**Clear cache**:
```bash
rm -rf data/cache/*        # Linux/Mac
del /Q data\cache\*        # Windows
mkdir data/cache           # Recreate if needed
```

#### Cache File Corruption

**Symptom**: Images don't load from cache

**Solutions**:
1. **Clear corrupted cache**: Delete cache directory contents
2. **Check permissions**: Ensure app can read/write cache
3. **Disk errors**: Run disk check utility

## Advanced Troubleshooting

### Debug Mode

#### Enable Debug Logging

For source installations, add debug logging:

```python
# Add to main.py
import logging
logging.basicConfig(level=logging.DEBUG, filename='debug.log')
```

**Check logs**:
```bash
tail -f debug.log    # Linux/Mac
type debug.log       # Windows
```

#### Verbose Error Messages

Run from command line to see full errors:

```bash
# Windows
unsplash-gpt-tool.exe --debug

# Source
python main.py --verbose
```

### Process Monitoring

#### Check System Resources

**Windows**:
- Task Manager → Processes tab
- Look for high CPU/Memory usage

**Linux/Mac**:
```bash
top -p $(pgrep -f unsplash)
ps aux | grep python
```

#### Network Monitoring

**Monitor API calls**:
```bash
# Linux
netstat -tulpn | grep python

# Windows  
netstat -an | findstr :443
```

### Testing API Endpoints

#### Manual API Testing

**Test Unsplash API**:
```bash
curl -H "Authorization: Client-ID YOUR_KEY" \
  "https://api.unsplash.com/search/photos?query=test&per_page=1" | python -m json.tool
```

**Test OpenAI API**:
```bash
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

### System Information

#### Collect System Info

**For bug reports, collect**:

```bash
# System info
uname -a                    # Linux/Mac
systeminfo                  # Windows

# Python info
python --version
pip list | grep -E '(tkinter|PIL|openai|requests)'

# Application info
ls -la config.ini
ls -la data/
```

## Getting Help

### Before Asking for Help

**Gather this information**:

1. **Operating system and version**
2. **Application version** (check About dialog or README)
3. **Installation method** (installer, portable, source)
4. **Exact error message** (screenshot if possible)
5. **Steps to reproduce** the problem
6. **What you've already tried**

### Support Channels

1. **GitHub Issues**: [Create new issue](https://github.com/your-username/unsplash-image-search-gpt-description/issues)
   - Best for bug reports and feature requests
   - Include system info and error logs

2. **GitHub Discussions**: [Community help](https://github.com/your-username/unsplash-image-search-gpt-description/discussions)
   - Best for usage questions
   - Search existing discussions first

3. **Documentation**: Check `docs/` folder
   - User manual
   - Installation guide
   - API setup guide

### Creating Good Bug Reports

**Include**:
- Clear title describing the problem
- Steps to reproduce
- Expected vs actual behavior
- System information
- Screenshots/error messages
- Relevant log files

**Template**:
```markdown
**Problem**: Brief description

**Environment**:
- OS: Windows 10 64-bit
- Version: v2.0.0 (installer)
- Python: 3.11.0 (if relevant)

**Steps to reproduce**:
1. Launch application
2. Search for "test"
3. Click "Generate Description"

**Expected**: Description should appear
**Actual**: Error message "API key not found"

**Error message**: [full error text]

**What I tried**:
- Checked config.ini exists
- Re-entered API keys
- Restarted application
```

### Self-Help Resources

1. **Built-in Help**: Press F1 in application
2. **README.md**: Basic usage and setup
3. **docs/ folder**: Comprehensive documentation
4. **GitHub Issues**: Search existing issues
5. **API Documentation**: Unsplash and OpenAI docs

---

## Quick Reference

### Emergency Reset

**If everything is broken**:
1. Close application
2. Backup `data/vocabulary.csv` (if important)
3. Delete `config.ini`
4. Delete `data/cache/` contents
5. Restart application
6. Re-run setup wizard

### Key File Locations

- **Config**: `config.ini` in app directory
- **Vocabulary**: `data/vocabulary.csv`
- **Sessions**: `data/session_log.json`
- **Cache**: `data/cache/` folder
- **Logs**: `debug.log` (if enabled)

### Essential Commands

```bash
# Test API keys
curl -H "Authorization: Client-ID YOUR_UNSPLASH_KEY" "https://api.unsplash.com/stats/total"
curl -H "Authorization: Bearer YOUR_OPENAI_KEY" "https://api.openai.com/v1/models"

# Check system resources
top                     # Linux/Mac
Task Manager            # Windows

# Clear cache
rm -rf data/cache/*     # Linux/Mac
del /Q data\cache\*     # Windows
```

---

**Still having issues?** Create a GitHub issue with detailed information about your problem, and we'll help you get it resolved!