import socket
import subprocess
import webbrowser
import os
import time
import platform

# --- CONFIGURATION ---
# Si tu es sur le même Wi-Fi, mets l'IP locale (192.168...)
# Si tu es à distance, mets l'IP Tailscale (100.x.y.z)
HOST = '192.168.1.XX' 
PORT = 65432
PASSWORD = "1234"

def execute_action(command):
    sys_type = platform.system()
    try:
        if command.startswith("popup:"):
            msg = command[6:]
            if sys_type == "Windows":
                subprocess.run(['powershell', '-Command', f'Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show("{msg}")'])
            else:
                subprocess.run(['notify-send', '📱 Alerte Ractt', msg])
            return "Notification affichée"

        elif command.startswith("speak:"):
            msg = command[6:]
            if sys_type == "Windows":
                subprocess.run(['powershell', '-Command', f'(New-Object -ComObject SAPI.SpVoice).Speak("{msg}")'])
            else:
                subprocess.run(['espeak-ng', '-v', 'fr', msg])
            return "Message vocal envoyé"

        elif command == "lock":
            if sys_type == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                os.system("xdg-screensaver lock")
            return "Écran verrouillé"

        elif command.startswith("browser:"):
            url = command[8:]
            if not url.startswith("http"): url = "https://" + url
            webbrowser.open(url)
            return f"Navigateur ouvert sur {url}"

        elif command == "battery":
            if sys_type == "Linux":
                with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
                    return f"Batterie : {f.read().strip()}%"
            return "Info batterie non supportée sur ce Windows"

        return "Commande reçue"
    except Exception as e:
        return f"Erreur : {str(e)}"

def main():
    print(f"[*] Client Ractt ({platform.system()}) en attente du serveur...")
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((HOST, PORT))
                
                if s.recv(1024).decode() == "AUTH_REQUIRED":
                    s.sendall(PASSWORD.encode())
                
                if s.recv(1024).decode() == "AUTH_SUCCESS":
                    print(f"[+] Connecté à {HOST} !")
                    s.settimeout(None)
                    while True:
                        data = s.recv(4096).decode()
                        if not data or data == "exit": break
                        rep = execute_action(data)
                        s.sendall(rep.encode())
        except Exception:
            # Reconnexion automatique si le serveur est coupé ou si on change de réseau
            time.sleep(5)

if __name__ == "__main__":
    main()
