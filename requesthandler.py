import base64
import json
import os
import uuid
import pathlib

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime


last_articles_refresh = datetime.now()
articles_db_data = None

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def get_client_ip(self):
        if self.headers.__contains__("PROXY"):
            if self.headers.__contains__("X-FORWARDED-FOR"):
                return self.headers.get("X-FORWARDED-FOR")
        else:
            return self.client_address[0]
        return None

    def do_GET(self):
        global last_articles_refresh
        global articles_db_data

        parsed_path = urlparse(self.path)
        splitted = parsed_path.path.split("/")
        if len(splitted) < 2:
            self.send_response(400)
            self.end_headers()
            return

        # update articles file if necessary
        articles_db_stat = pathlib.Path("./articles/db.json").stat()
        if articles_db_stat.st_mtime != last_articles_refresh:
            with open("./articles/db.json") as articles_db_file:
                articles_db_data = json.load(articles_db_file)
            last_articles_refresh = articles_db_stat.st_mtime

        if splitted[1] == "articles":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(articles_db_data).encode())

        elif splitted[1] == "article_file":
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=UTF-8")
            self.send_header(
                "Content-Length",
                str(os.stat("./articles/files/" + splitted[2]).st_size),
            )
            self.send_header("Content-Disposition", "inline")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open("./articles/files/" + splitted[2], "rb") as article_file:
                self.wfile.write(article_file.read())    
        
        else:
            self.send_response(401)
            self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        parsed_query = parse_qs(parsed_path.query)
        if parsed_path.path.startswith("/contactform"):                  
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            import smtplib

            content_len = int(self.headers.get("Content-Length"))
            post_content = self.rfile.read(content_len)

            gmail_user = "tipfom.pok@gmail.com"
            gmail_password = "idiubpukwfnzthui"
            sent_from = gmail_user
            to = ["timpokart@outlook.de"]
            subject = "Website Contact Form"
            body = post_content

            email_text = f"""
            From: {sent_from}
            To: {", ".join(to)}
            Subject: {subject}
            Name: {parsed_query["name"][0]}
            E-mail: {parsed_query["mail"][0]}
            {body.decode()}"""

            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(sent_from, to, email_text)
                server.close()
                self.wfile.write("success".encode())
            except:
                self.wfile.write("error".encode())

        else:
            self.send_response(401)
            self.end_headers()
