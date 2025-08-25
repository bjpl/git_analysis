# Deployment Guide for Number Sense 3s

## 🚀 Quick Deployment Options

### 1. GitHub Pages (Recommended - Free & Easy)

#### Step-by-Step Instructions:

1. **Create a GitHub Account** (if you don't have one)
   - Go to [github.com](https://github.com)
   - Click "Sign up"
   - Follow the registration process

2. **Fork or Upload This Repository**
   
   **Option A: Fork (if viewing on GitHub)**
   - Click the "Fork" button at the top right
   - This creates your own copy

   **Option B: Upload Your Files**
   - Click the "+" icon in the top right
   - Select "New repository"
   - Name it `number-sense-3s`
   - Set to Public
   - Don't initialize with README
   - Click "Create repository"
   - Follow the instructions to upload files:
     ```bash
     git init
     git add .
     git commit -m "Initial upload"
     git branch -M main
     git remote add origin https://github.com/YOURUSERNAME/number-sense-3s.git
     git push -u origin main
     ```
   
   **Option C: Upload via GitHub Website**
   - Create new repository (as above)
   - Click "uploading an existing file"
   - Drag all project files into the browser
   - Click "Commit changes"

3. **Enable GitHub Pages**
   - Go to your repository
   - Click "Settings" tab
   - Scroll down to "Pages" in the left sidebar
   - Under "Source", select "Deploy from a branch"
   - Choose "main" branch
   - Select "/ (root)" folder
   - Click "Save"

4. **Access Your Site**
   - Wait 2-5 minutes for deployment
   - Your site will be available at:
   ```
   https://YOURUSERNAME.github.io/number-sense-3s/
   ```
   - Share this link with students!

### 2. Netlify (Alternative - Also Free)

1. **No GitHub Required Method:**
   - Go to [netlify.com](https://www.netlify.com)
   - Sign up for free account
   - Click "Add new site" → "Deploy manually"
   - Drag your project folder into the browser
   - Your site is instantly live!
   - Get a custom URL like: `amazing-teacher-123.netlify.app`

2. **With GitHub:**
   - Connect your GitHub account
   - Select your repository
   - Auto-deploys when you update!

### 3. Local Network (School Computers)

#### For Teachers/IT Staff:

1. **Copy to Network Drive:**
   ```
   \\SchoolServer\SharedDrive\Educational\NumberSense3s\
   ```

2. **Create Desktop Shortcut:**
   - Right-click on desktop
   - New → Shortcut
   - Browse to `index-modern.html`
   - Name it "Number Sense 3s"

3. **Multiple Computer Setup:**
   - Use a batch file to copy to all computers:
   ```batch
   @echo off
   xcopy "\\Server\NumberSense3s" "C:\Educational\NumberSense3s\" /E /Y
   echo Shortcut created on Desktop
   ```

### 4. Google Drive Hosting

1. **Upload to Google Drive:**
   - Create folder "NumberSense3s"
   - Upload all files
   - Keep folder structure intact

2. **Share with Students:**
   - Right-click folder → Share
   - Set to "Anyone with link can view"
   - Students download and open locally

### 5. School Website Integration

#### For Web Administrators:

1. **Upload via FTP:**
   ```bash
   ftp school.edu
   cd public_html/tools/
   mkdir number-sense-3s
   cd number-sense-3s
   put -r *
   ```

2. **Create Link on School Site:**
   ```html
   <a href="/tools/number-sense-3s/" class="btn">
     Number Sense 3s Learning Tool
   </a>
   ```

### 6. USB Drive Distribution

Perfect for computer labs without internet:

1. **Prepare USB Drives:**
   - Copy entire folder to USB
   - Create `RUN_ME.bat` file:
   ```batch
   @echo off
   start index-modern.html
   ```

2. **Student Instructions:**
   - Insert USB
   - Double-click "RUN_ME"
   - Tool opens in browser

## 📱 Mobile Deployment

### For iPads/Tablets (School Managed):

1. **Using MDM (Mobile Device Management):**
   - Deploy as web clip
   - URL: Your GitHub Pages link
   - Icon provided in `/assets/icon.png`

2. **Manual Setup:**
   - Open Safari/Chrome
   - Navigate to your GitHub Pages URL
   - Tap Share → "Add to Home Screen"
   - Name it "Number Sense 3s"

## 🔒 Security & Privacy

### For School IT Departments:

**This tool is safe because:**
- ✅ No external dependencies
- ✅ No tracking or analytics
- ✅ All data stored locally
- ✅ No server communication
- ✅ Open source code
- ✅ COPPA compliant (no data collection)

**Firewall/Proxy Settings:**
- No special configuration needed
- Works entirely offline once loaded
- Only needs initial HTTP/HTTPS access

## 🖥️ System Requirements

**Minimum:**
- Any browser from 2018+
- 512MB RAM
- No installation needed

**Recommended:**
- Chrome, Firefox, Safari, or Edge (latest)
- 2GB RAM for smooth animations
- Screen resolution: 1024×768 or higher

## 📊 Classroom Setup Tips

### Computer Lab (30 stations):

1. **Quick Deploy Script:**
```powershell
# PowerShell script for Windows labs
$source = "\\server\share\number-sense-3s"
$computers = Get-Content "lab-computers.txt"

foreach ($computer in $computers) {
    Copy-Item $source "\\$computer\c$\Users\Public\Desktop\" -Recurse
    Write-Host "Deployed to $computer"
}
```

2. **Create Shared Bookmark:**
   - Deploy via Group Policy
   - Or manually on each browser

### For Remote Learning:

1. **Share link via:**
   - Google Classroom
   - Canvas/Blackboard
   - Email to parents
   - QR code on handouts

2. **QR Code Generation:**
   - Go to [qr-code-generator.com](https://www.qr-code-generator.com)
   - Enter your GitHub Pages URL
   - Print for worksheets

## 🔧 Troubleshooting Deployment

### GitHub Pages Not Working?
- Check repository is public
- Verify Pages is enabled in Settings
- Wait 10 minutes for DNS propagation
- Try hard refresh (Ctrl+F5)

### School Firewall Blocking?
- Request whitelist for `github.io`
- Use alternative domain (Netlify)
- Deploy to school's own server

### Slow Loading?
- Use the minified version
- Disable animations in settings
- Check network speed
- Consider local deployment

## 📝 Deployment Checklist

Before deploying, ensure:
- [ ] Tested in target browser
- [ ] Checked all game modes work
- [ ] Verified offline functionality
- [ ] Tested on target devices
- [ ] Created backup of original files
- [ ] Documented deployment URL
- [ ] Shared access instructions
- [ ] Tested with sample student account

## 💡 Pro Tips

1. **Custom Domain:**
   - Use `math-tools.school.edu` instead of GitHub URL
   - Configure in GitHub Pages settings

2. **Analytics (Optional):**
   - Add Google Analytics for usage stats
   - Ensure COPPA compliance first

3. **Updates:**
   - GitHub Pages auto-updates on push
   - Notify users of major updates

4. **Backup:**
   - Keep local copy
   - Export student data regularly
   - Use version control

## 📧 Support

Need help deploying? Common resources:
- GitHub Pages Docs: https://pages.github.com
- Your school's IT helpdesk
- Create an issue on GitHub
- Check README.md for more info

---

**Remember:** The tool works 100% offline once loaded, making it perfect for schools with limited internet!