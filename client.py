import socket
import subprocess
import webbrowser
import os
import time
import platform

# --- CONFIGURATION ---
HOST = '192.168.1.XX' # <--- METS L'IP DE TON TEL (OU PC SERVEUR) ICI
PORT = 65432
PASSWORD = "1234"

def execute_action(command):
    systeme = platform.system() # "Windows" ou "Linux"
    try:
        if command.startswith("popup:"):
            txt = command[6:]
            if systeme == "Windows":
                subprocess.run(['powershell', '-Command', f'Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show("{txt}")'])
            else: # Linux (Bazzite/Fedora)
                subprocess.run(['notify-send', '📱 Alerte Mobile', txt])
            return "Notification affichée"

        elif command.startswith("speak:"):
            txt = command[6:]
            if systeme == "Windows":
                subprocess.run(['powershell', '-Command', f'(New-Object -ComObject SAPI.SpVoice).Speak("{txt}")'])
            else: # Linux
                subprocess.run(['espeak-ng', '-v', 'fr', txt])
            return "Message vocal réussi"

        elif command == "lock":
            if systeme == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else: # Linux
                os.system("xdg-screensaver lock")
            return "PC verrouillé"

        elif command == "battery":
            if systeme == "Linux":
                with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
                    return f"Batterie : {f.read().strip()}%"
            return "Info batterie non disponible sur ce Windows"

        elif command.startswith("browser:"):
            webbrowser.open(command[8:])
            return "URL ouverte"

        return "Commande inconnue"
    except Exception as e:
        return f"Erreur : {str(e)}"

def main():
    print(f"[*] Client PC ({platform.system()}) en attente de connexion...")
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((HOST, PORT))
                
                # Authentification
                if s.recv(1024).decode() == "AUTH_REQUIRED":
                    s.sendall(PASSWORD.encode())
                
                if s.recv(1024).decode() == "AUTH_SUCCESS":
                    print(f"[+] Connecté au serveur ({HOST})")
                    s.settimeout(None)
                    while True:
                        data = s.recv(4096).decode()
                        if not data or data == "exit": break
                        resultat = execute_action(data)
                        s.sendall(resultat.encode())
        except:
            # Attend 5 secondes avant de réessayer si le serveur est absent
            time.sleep(5)

if __name__ == "__main__":
    main()
