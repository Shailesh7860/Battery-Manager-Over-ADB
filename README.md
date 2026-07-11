# 📱 Wireless Battery Management System: Operations Manual

This system monitors a **Android** over Wi-Fi from a **Raspberry Pi** and software-throttles the battery charging loop between **30% and 80%** without risking your connected hard drive.

---

## 🛠️ Section 1: System Files Reference

### 1. The Python Script Location
* **Path:** `/root/battery_manager.py`
* **Purpose:** Queries the phone every 5 minutes and dynamically flips the Android system status between normal charging (`dumpsys battery reset`) and battery idle mode (`dumpsys battery set status 4`).

### 2. The Linux Background Service
* **Path:** `/etc/systemd/system/battery-monitor.service`
* **Purpose:** Keeps the script running 24/7 in the background and restarts it automatically if the Raspberry Pi reboots or crashes.

---

## 📋 Section 2: Essential Commands Directory

Keep these commands handy for checking and managing your setup.

### To View Live Logs (Watch the percentage updates)
```bash
sudo journalctl -u battery-monitor.service -f -n 20
```

### To Restart the Monitor Engine
```bash
sudo systemctl restart battery-monitor.service
```

### To Stop the Monitor Engine Permanently
```bash
sudo systemctl stop battery-monitor.service
```

### To Verify Phone Connection Manually
```bash
adb devices
```

---

## ⚠️ Section 3: Critical Recovery Manual (When things break)

Because this setup uses a **charge-only wire** and a wireless network pipe, certain events will require manual recovery steps.

### Scenario A: The Phone Power Dies (Hits 0%)
If the phone battery completely runs out of juice or shuts down, it will **wipe the wireless ADB settings from its RAM**.
1. **Unplug** the phone from the charge-only wire.
2. **Plug it into a wall charger** or your Pi using a **temporary data-capable cable** for 10 minutes to boot it back up.
3. Once booted, open the Pi terminal and run the wireless handshake reset:
   ```bash
   adb tcpip 5555
   ```
4. Disconnect the data cable, plug the **charge-only wire** back in, and run:
   ```bash
   adb connect 192.168.x.x:5555
   ```
5. Restart your service: 
   ```bash
   sudo systemctl restart battery-monitor.service
   ```

### Scenario B: You Get a New Wi-Fi Router or the Phone's IP Address Changes
If your home internet router restarts or changes, your phone might be assigned a new network IP address (e.g., `192.168.0.105`). The script will look for the old IP and report it as unreachable.
1. On your phone, go to **Settings > About Phone > Status** and look up the new **IP address**.
2. Open your Python script on the Pi:
   ```bash
   sudo nano /root/battery_manager.py
   ```
3. Change the `PHONE_IP` line at the very top to your new IP address.
4. Save and close (`Ctrl+O`, then `Ctrl+X`).
5. Run the new wireless connect command:
   ```bash
   adb connect NEW_PHONE_IP:5555
   ```
6. Restart the engine: 
   ```bash
   sudo systemctl restart battery-monitor.service
   ```

---

## ⚙️ Section 4: Required Phone Settings (Never Turn These Off)

To keep the wireless background connection stable over long periods, make sure your Redmi 6A stays configured with these exact developer adjustments:

* **Stay Awake:** Go to *Settings > Developer Options* and ensure **Stay Awake (Screen will never sleep while charging)** is turned **ON**. This stops the phone from falling into a deep standby sleep that kills the network card.
* **Wi-Fi Sleep Policy:** Go to *Settings > Wi-Fi > Additional Settings* and ensure **Keep Wi-Fi on during sleep** is set to **Always**. 
* **MIUI Battery Optimization:** Go to *Settings > Battery & Performance > Manage apps battery usage*, locate the *System Android/ADB subsystem*, and set it to **No Restrictions**. This prevents MIUI's aggressive software layer from killing the background wireless listening port.

---

## 🛒 Section 5: Future Hardware Upgrades (Optional)

If your wireless network ever becomes too crowded or unstable, you can transition this configuration away from Wi-Fi communication by picking up a cheap **Smart USB Hub with Per-Port Power Switching (PPPS)**. 

With a PPPS hub, you can switch back to a standard **data cable**, plug your hard drive into one hub slot, your phone into another, and use the `uhubctl` tool to cut the physical electricity to the phone's port without touching or interrupting your hard drive.
