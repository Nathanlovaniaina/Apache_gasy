import socket
import os
import threading
import subprocess
from ResponseHTTPFormateur import ResponseHTTPFormateur

# Dossier racine du serveur
ROOT_DIR = "./www"
PORT = 3355

def list_files(path):
    """Retourne une page HTML avec la liste des fichiers du dossier"""
    files = os.listdir(path)
    file_list_html = ""
    for file in files:
        # Créer un lien vers chaque fichier/dossier
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            file_list_html += f"<li><a href='{file}/'>{file}/</a></li>"
        else:
            file_list_html += f"<li><a href='{file}'>{file}</a></li>"
    
    return f"""
    <html>
    <body>
        <h1>Index de {path}</h1>
        <ul>
            {file_list_html}
        </ul>
    </body>
    </html>
    """

def handle_client(client_socket):
    try:
        # Lire la requête
        request = client_socket.recv(1024).decode()
        if not request:
            client_socket.close()
            return

        # Extraire la méthode et le chemin demandé
        print(f"La requête est {request}")
        interpreteur = ResponseHTTPFormateur()
        response = interpreteur.get_HTTP_response(request)
        tete = response.get("tete")
        body = response.get("body")
        client_socket.send(tete.encode())
        if isinstance(body, str):
            client_socket.send(body.encode())
        else:
            client_socket.send(body)

    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        client_socket.close()

# Démarrer le serveur
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(5)
    print(f"Serveur démarré sur le port {PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connexion reçue de {addr}")
        # Gérer chaque client dans un thread séparé
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
