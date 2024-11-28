import mimetypes
import os
import subprocess
from urllib.parse import urlparse

class ResponseHTTPFormateur:

    def __init__(self) -> None:
        self.tab_content_type = {
    # Textes
    ".php": "text/html",
    ".css": "text/css",
    ".jsp": "text/html",
    ".js": "text/javascript",

    # Images
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".tiff": "image/tiff",
    ".heic": "image/heic",

    # Musiques
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
    ".m4a": "audio/mp4",

    # Vidéos
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".flv": "video/x-flv",
    ".wmv": "video/x-ms-wmv",
    ".3gp": "video/3gpp",
    ".mpeg": "video/mpeg"
}

        self.projects_path = "./www"



#--------------------------------------------------------------------------------------

    def list_files(self,path):
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

#-----------------------------------------------------------------------------------

    def get_HTTP_response(self, requete_HTTP):
        print(f"La requête est : {requete_HTTP}")

        request_line = requete_HTTP.split("\r\n")[0]

        try:
            method, path, _ = request_line.split()
        except ValueError:
            return "Requête mal formée"

        _, extension = os.path.splitext(path)
        headers =requete_HTTP.split("\r\n\r\n")[0]  
        response =""
        body =requete_HTTP.split("\r\n\r\n")[1] if "\r\n\r\n" in requete_HTTP else ""
        parsed_url = urlparse(path)
        file_path = os.path.join(self.projects_path, parsed_url.path.lstrip("/"))  

        if os.path.isdir(file_path):
            response_body = self.list_files(file_path)
            content_type = "text/html"

            response= (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(response_body)}\r\n"
            )
            result = {"tete":response,
                "body":response_body}

        elif os.path.exists(file_path):
            if file_path.endswith(".php"):
                env = os.environ.copy()
                env["REQUEST_METHOD"] = method
                env["QUERY_STRING"] = parsed_url.query  # Passer les paramètres GET
                if method == "POST":
                    env["CONTENT_LENGTH"] = str(len(body))
                process = subprocess.run(
                    ["php", file_path],
                    input=body if method == "POST" else None,
                    capture_output=True,
                    text=True,
                    env=env
                )
                response_body = process.stdout
            else:
                # Lire un fichier statique (CSS, JS, HTML, etc.)
                with open(file_path, "rb") as file:
                    response_body = file.read()
                
            
            content_type = self.tab_content_type.get(extension)
            print(content_type)
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"\r\n"
            )
            result = {"tete":response,
                "body":response_body}

        else:
            # Réponse HTTP 404 Not Found
            response_body = "<h1>404 Not Found</h1>"
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
            )
            result = {"tete":response,
                "body":response_body}
        return result


#if __name__ == "__main__":
#    test = ResponseHTTPFormateur()
#    requete = "GET /DigitalMedia/ HTTP/1.1"
#    #requete = "GET / HTTP/1.1"
#    resultat = test.get_HTTP_response(requete)

#   print(resultat)
