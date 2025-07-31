# pass_ex
This code is designed to steal browser passwords, clipboard data, and system information, then exfiltrate that sensitive data via email.

# 🦉 Browser Credential Extraction Tool (For Educational Purposes)

**Version:** 1.0  
**Platform:** Windows  

---

## 🚨 LEGAL WARNING

> **This tool is strictly for educational, research, and security awareness demonstrations on systems you *own* or have *explicit written permission* to audit. _Unauthorized running of this software is illegal and unethical!_ The authors disclaim all liability for misuse.**

---

## 🎯 What Is This Tool?

This Python-based script demonstrates how browser-stored credentials, basic system information, and clipboard data can be programmatically harvested **from a Windows user account** and securely exported via email.  
The data is written to a stealth location (`SysDataHidden`) and automatically sent to a user-specified mail address before the trace file is deleted.

**It illustrates:**
- Real-world security risks when local machines are compromised (for blue teams & educators).
- How browsers store and encrypt saved passwords on disk.
- The importance of endpoint and credential hygiene.

---

## 🤹‍♂️ Key Features

- 🕵️‍♂️ Extracts Chrome, Edge, Opera, Opera GX, and Brave saved credentials.
- 💡 Decrypts passwords using system APIs (as browsers would).
- 🖥️ Collects OS and network fingerprint information.
- 📋 Reads clipboard contents (what’s currently copied).
- 🤫 Report file is saved to a _hidden_ OS folder, then deleted after emailing.
- ✉️ Data is emailed to a trusted mailbox via secure Gmail SMTP.

---

## 🚀 Usage Guide

### 1. **Requirements**

- Windows 10/11 system.
- Python 3.7+ (tested up to 3.11+).
- The following modules installed:  
  ```
    pip install pyperclip pycryptodome requests pypiwin32
  ```
- Gmail account with [App Passwords](https://myaccount.google.com/apppasswords) (when 2-Step Verification enabled).

---

### 2. **Setup**

Edit these lines at the top of `main.py`:

SENDER_EMAIL = "your-gmail@gmail.com" # Your Gmail address
APP_PASSWORD = "abcd efgh ijkl mnop" # Gmail App Password (not your real password!)
RECIPIENT_EMAIL = "your-gmail@gmail.com" # Where to send the loot.dat



**_Never share your real password. Always use an App Password for scripts!_**

---

### 3. **Run the Script**

- **Via Terminal:**  
  ```
  python info.py
  ```

- **To create an .exe (no console):**
-  
  1. Install PyInstaller:  
     ```
     pip install pyinstaller
     ```
     
  3. Build:  
     ```
     pyinstaller --onefile --windowed info.py
     ```
     
  5. Find the executable in `/dist`.

---

### 4. **View The Results**

- Check the email inbox set in `RECIPIENT_EMAIL` for the attached `loot.dat`.
- File contents will include all extracted browser credentials, system info, and clipboard data at the time of execution.
- The loot file is auto-deleted from disk after being sent.

---

## 🌟 Educational Tips

- Try running the script with/without browsers open to see what changes in extraction results.
- Review **loot.dat** contents and spot the sensitive data exposed.
- Use this exercise to teach defense:  
  - The risk of unlocked user sessions  
  - Why to avoid storing passwords in browsers  
  - The importance of endpoint protections (anti-malware, EDR, OS security).

---

## ⚠️ Responsible Use

- **Do NOT run on other people's devices or networks.**
- **Do NOT send extracted data over untrusted channels or third-party systems.**
- Inform users *before* running any extraction demos.
- Delete all loot files from your environment after teaching.

---

## ✍️ License

This is a demonstration and teaching script provided "AS IS".  
You are responsible for any use, authorized or unauthorized.

---

##### 👨‍💻 _Curious about how credential decryption works? Explore the code and learn how browsers’ local security is both a strength and a risk!_



