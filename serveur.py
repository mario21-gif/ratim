import socket
import platform

# --- CONFIGURATION ---
PORT = 65432
PASSWORD = "1234"

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('0.0.0.0', PORT))
            s.listen(1)
            print(f"--- RACTT SERVER CENTRAL ---")
            print(f"[*] Système : {platform.system()}")
            print(f"[*] Port d'écoute : {PORT}")
            print("[*] En attente d'une connexion mondiale...")
        except Exception as e:
            print(f"[!] Erreur de démarrage : {e}")
            return

        conn, addr = s.accept()
        with conn:
            print(f"\n[+] APPAREIL DISTANT CONNECTÉ : {addr[0]}")
            
            # Authentification sécurisée
            conn.sendall(b"AUTH_REQUIRED")
            auth = conn.recv(1024).decode().strip()
            
            if auth == PASSWORD:
                conn.sendall(b"AUTH_SUCCESS")
                print("[OK] Accès autorisé. Tapez 'help' pour les options.")
                
                while True:
                    cmd = input(f"\n({addr[0]}) > ").strip()
                    if not cmd: continue
                    
                    if cmd.lower() == "help":
                        print("""
    AIDE COMMANDES :
    - popup:message  -> Affiche une bulle sur le PC
    - speak:message  -> Le PC parle (français)
    - browser:url    -> Ouvre un site (ex: browser:youtube.com)
    - lock           -> Verrouille le PC
    - battery        -> Voir le niveau de batterie (Linux)
    - exit           -> Fermer la connexion
                        """)
                        continue
                    
                    conn.sendall(cmd.encode())
                    if cmd == "exit": break
                    
                    try:
                        reponse = conn.recv(4096).decode()
                        print(f"[PC DISTANT] : {reponse}")
                    except:
                        print("[!] Connexion interrompue.")
                        break
            else:
                print("[-] Mot de passe incorrect.")

if __name__ == "__main__":
    start_server()
