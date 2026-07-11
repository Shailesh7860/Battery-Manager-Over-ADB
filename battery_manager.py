import subprocess
import time
import sys

# --- CONFIGURATION ---
PHONE_IP = "192.168.x.x:5555"
MAX_BATTERY = 80
MIN_BATTERY = 30
CHECK_INTERVAL = 300  # 5 minutes

def run_cmd(command):
    """Executes a command with a strict 3-second network timeout to prevent hanging."""
    try:
        # timeout=3 prevents the script from locking up if Wi-Fi fluctuates
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=3)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception:
        return ""

def heal_adb_connection():
    """Safely pings the phone over Wi-Fi without restarting the ADB server engine."""
    devices = run_cmd("adb devices")
    if PHONE_IP not in devices or "device" not in devices or "TIMEOUT" in devices:
        print(f"[*] [{time.strftime('%H:%M:%S')}] Wi-Fi link unstable. Pinging {PHONE_IP}...", flush=True)
        run_cmd(f"adb connect {PHONE_IP}")
        time.sleep(2)
    
    devices_check = run_cmd("adb devices")
    return PHONE_IP in devices_check and "device" in devices_check

def get_battery_level():
    """Queries phone battery with absolute timeout protection."""
    output = run_cmd(f"adb -s {PHONE_IP} shell dumpsys battery | grep level")
    
    if not output or "error" in output.lower() or "TIMEOUT" in output:
        heal_adb_connection()
        output = run_cmd(f"adb -s {PHONE_IP} shell dumpsys battery | grep level")
        
    if output and "level:" in output:
        try:
            return int(output.split(":")[-1].strip())
        except ValueError:
            return None
    return None

def manage_charging():
    print(f"[+] [{time.strftime('%H:%M:%S')}] Launching Wireless Monitor Engine...", flush=True)
    charging_disabled = False
    heal_adb_connection()

    while True:
        level = get_battery_level()
        
        if level is None:
            print(f"[!] [{time.strftime('%H:%M:%S')}] Phone unreachable over Wi-Fi. Retrying in 30s...", flush=True)
            time.sleep(30)
            continue
            
        print(f"[*] [{time.strftime('%H:%M:%S')}] Battery: {level}%", flush=True)
        
        # Boundary logic
        if level >= MAX_BATTERY and not charging_disabled:
            print(f"[+] [{time.strftime('%H:%M:%S')}] Battery High ({level}%). Halting power input...", flush=True)
            res = run_cmd(f"adb -s {PHONE_IP} shell dumpsys battery set status 4")
            if "error" not in res.lower() and "TIMEOUT" not in res:
                charging_disabled = True
            
        elif level <= MIN_BATTERY and charging_disabled:
            print(f"[-] [{time.strftime('%H:%M:%S')}] Battery Low ({level}%). Resuming power input...", flush=True)
            res = run_cmd(f"adb -s {PHONE_IP} shell dumpsys battery reset")
            if "error" not in res.lower() and "TIMEOUT" not in res:
                charging_disabled = False
                
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        manage_charging()
    except KeyboardInterrupt:
        run_cmd(f"adb -s {PHONE_IP} shell dumpsys battery reset")
        sys.exit(0)
