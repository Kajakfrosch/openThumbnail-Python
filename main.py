import base64
import logging
import threading
from flask import Flask, jsonify, request, Response
import couchdb
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)
import json

# JSON-Konfiguration laden
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
# Tokens und andere Konfigurationen aus der Datei laden
SECURITY_TOKENS = config_data['security_tokens']
COUCHDB_SERVER = config_data['couchdb_server']
DATABASE_NAME = config_data['database_name']


# Dummy Security Token für die Validierung
SECURITY_TOKEN = "my_secure_token_123"


db_lock = threading.Lock()

class CouchDBHandler:

    def __init__(self):
        self.server = couchdb.Server(COUCHDB_SERVER)
    def create_clip_id_view(self):
        try:
            db = self.server[DATABASE_NAME]
            design_doc_id = "_design/clip_id_index"
            if design_doc_id not in db:
                # Design-Dokument mit View erstellen
                design_doc = {
                    "_id": design_doc_id,
                    "views": {
                        "by_clip_id": {
                            "map": "function(doc) { \
                                if (doc.clip_id) { emit(doc.clip_id, { _id: doc._id }); } \
                            }"
                        }
                    }
                }
                db.save(design_doc)
                print("Design-Document successfully created!")
            else:
                print("Design-Document already exists!")
        except Exception as e:
            print(f"Error while creating the View: {e}")
    # Methode: Dokumente und Attachments für clip_id abrufen
        def add_attachment(self, clip_id, page, doc_id, file):
            try:
                db = self.server[DATABASE_NAME]

                # Dokument überprüfen
                if doc_id not in db:
                    return {"error": f"Dokument mit ID {doc_id} wurde nicht gefunden."}, 404

                # Bildverkleinerung mit Pillow
                if file.mimetype == 'image/jpeg':  # Überprüfung auf JPEG
                    image = Image.open(file)
                    image = image.resize((200, 200))  # Verkleinerung auf 200x200 px
                    output = BytesIO()
                    image.save(output, format="JPEG")
                    output.seek(0)  # Position auf Anfang setzen
                    file_data = output.read()
                    output.close()
                else:
                    return {"error": "Nur JPEG-Dateien werden unterstützt."}, 400

                # Name des Anhangs erstellen (basiert auf Clip-ID und Seite)
                attachment_name = f"{clip_id}_page{page}.jpg"

                # Anhang hinzufügen
                db.put_attachment(
                    db[doc_id], file_data, filename=attachment_name, content_type="image/jpeg"
                )
                return {"message": f"Anhang {attachment_name} erfolgreich zu Dokument {doc_id} hinzugefügt."}, 201
            except Exception as e:
                return {"error": str(e)}, 500
        def create_clip_id_view(self):
            try:
                db = self.server[DATABASE_NAME]
                design_doc_id = "_design/clip_id_index"
                if design_doc_id not in db:
                    # Design-Dokument mit View erstellen
                    design_doc = {
                        "_id": design_doc_id,
                        "views": {
                            "by_clip_id": {
                                "map": "function(doc) { \
                                if (doc.clip_id) { emit(doc.clip_id, { _id: doc._id }); } \
                            }"
                            }
                        }
                    }
                    db.save(design_doc)
                    print("Design-Document successfully created!")
                else:
                    print("Design-Document already exists!")
            except Exception as e:
                print(f"Error while creating the View: {e}")

    # Methode: Dokumente und Attachments für clip_id abrufen
    def get_documents_and_attachments(self, clip_id):
        try:
            db = self.server[DATABASE_NAME]

            # Abfrage per View: Dokumente mit clip_id
            documents = [
                row.value for row in db.view('clip_id_index/by_clip_id', key=clip_id)
            ]

            # Wenn keine Dokumente gefunden wurden
            if not documents:
                return {"error": f"Keine Dokumente mit clip_id {clip_id} gefunden."}, 404

            results = []
            for doc in documents:
                doc_id = doc["_id"]
                document_with_attachments = db.get(doc_id, attachments=True)

                attachments = []

                # Inhalte der Attachments abrufen (falls vorhanden)
                if "_attachments" in document_with_attachments:
                    for attachment_name, attachment_info in document_with_attachments["_attachments"].items():
                        # Abrufen des Attachment-Inhalts
                        attachment_content = db.get_attachment(doc_id, attachment_name)
                        attachments.append({
                            "name": attachment_name,
                            "content_type": attachment_info["content_type"],
                            "data": base64.b64encode(attachment_content.read()).decode('utf-8')  # Base64-String
                        })
                results.append({
                    "document_id": doc_id,
                    "clip_id": clip_id,
                    "attachments": attachments
                })

            return {"documents": results}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def get_documents_by_clip_id(self, clip_id):
        try:
            db = self.server[DATABASE_NAME]

            # Abrufen von Dokumenten mit clip_id über den View
            documents = [
                row.value for row in db.view('clip_id_index/by_clip_id', key=clip_id)
            ]

            if not documents:
                return {"error": f"Keine Dokumente mit clip_id {clip_id} gefunden."}, 404

            # Gefundene Dokumente zurückgeben
            return {"documents": documents}, 200
        except couchdb.http.ResourceNotFound:
            return {"error": "Datenbank oder View wurde nicht gefunden."}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    # Beispiel mit der richtigen Definition
    def add_attachment(self, clip_id, page, doc_id, file):
        try:
            db = self.server[DATABASE_NAME]

            # Dokument überprüfen
            if doc_id not in db:
                return {"error": f"Dokument mit ID {doc_id} wurde nicht gefunden."}, 404

            # Bildverkleinerung mit Pillow
            try:
                if file.mimetype == 'image/jpeg':
                    image = Image.open(file)
                    image = image.resize((200, 200))  # Verkleinerung auf 200x200 px
                    output = BytesIO()
                    image.save(output, format="JPEG")
                    output.seek(0)  # Position auf Anfang setzen
                    file_data = output.read()
                    output.close()
                else:
                    return {"error": "Nur JPEG-Dateien werden unterstützt."}, 400
            except Exception as e:
                # Logging für Debugging
                logger.error(f"Fehler beim Verarbeiten der Bilddatei: {str(e)}")
                return {"error": f"Fehler beim Verarbeiten der Datei: {str(e)}"}, 500

            # Name des Anhangs erstellen (basiert auf Clip-ID und Seite)
            attachment_name = f"{clip_id}_page{page}.jpg"

            # Anhang hinzufügen
            db.put_attachment(
                db[doc_id], file_data, filename=attachment_name, content_type="image/jpeg"
            )
            return {"message": f"Anhang {attachment_name} erfolgreich zu Dokument {doc_id} hinzugefügt."}, 201
        except Exception as e:
            logger.error(f"Fehler in add_attachment: {str(e)}")
            return {"error": str(e)}, 500


def get_documents_and_attachments(self, clip_id):
    try:
        db = self.server[DATABASE_NAME]

        # Abfrage per View: Dokumente mit clip_id
        documents = [
            row.value for row in db.view('clip_id_index/by_clip_id', key=clip_id)
        ]

        # Wenn keine Dokumente gefunden wurden
        if not documents:
            return {"error": f"Keine Dokumente mit clip_id {clip_id} gefunden."}, 404

        results = []
        for doc in documents:
            doc_id = doc["_id"]
            document_with_attachments = db.get(doc_id, attachments=True)

            attachments = []

            # Inhalte der Attachments abrufen (falls vorhanden)
            if "_attachments" in document_with_attachments:
                for attachment_name, attachment_info in document_with_attachments["_attachments"].items():
                    # Abrufen des Attachment-Inhalts
                    attachment_content = db.get_attachment(doc_id, attachment_name)
                    attachments.append({
                        "name": attachment_name,
                        "content_type": attachment_info["content_type"],
                        "data": base64.b64encode(attachment_content.read()).decode('utf-8')  # Base64-String
                    })
            results.append({
                "document_id": doc_id,
                "clip_id": clip_id,
                "attachments": attachments
            })

        return {"documents": results}, 200

    except Exception as e:
        return {"error": str(e)}, 500

    def get_documents_by_clip_id(self, clip_id):
        try:
            db = self.server[DATABASE_NAME]

            # Abrufen von Dokumenten mit clip_id über den View
            documents = [
                row.value for row in db.view('clip_id_index/by_clip_id', key=clip_id)
            ]

            if not documents:
                return {"error": f"Keine Dokumente mit clip_id {clip_id} gefunden."}, 404

            # Gefundene Dokumente zurückgeben
            return {"documents": documents}, 200
        except couchdb.http.ResourceNotFound:
            return {"error": "Datenbank oder View wurde nicht gefunden."}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    def add_document(self, clip_id, page, doc_id):
        try:
            db = self.server[DATABASE_NAME]
            # Einfügen eines neuen Dokuments mit den übergebenen Feldern
            doc = {"clip_id": clip_id, "page": page}
            result = db.save(doc)
            return {"message": f"Dokument mit ID {result[1]} erfolgreich hinzugefügt."}, 201
        except Exception as e:
            return {"error": str(e)}, 500

    def add_attachment(self, clip_id, page, doc_id, file):
        try:
            db = self.server[DATABASE_NAME]

            # Dokument überprüfen
            if doc_id not in db:
                return {"error": f"Dokument mit ID {doc_id} wurde nicht gefunden."}, 404

            # Bildverkleinerung mit Pillow
            if file.mimetype == 'image/jpeg':
                image = Image.open(file)
                image = image.resize((200, 200))  # Verkleinerung auf 200x200 px
                output = BytesIO()
                image.save(output, format="JPEG")
                output.seek(0)  # Position auf Anfang setzen
                file_data = output.read()
                output.close()
            else:
                return {"error": "Nur JPEG-Dateien werden unterstützt."}, 400

            # Name des Anhangs erstellen (basiert auf Clip-ID und Seite)
            attachment_name = f"{clip_id}_page{page}.jpg"

            # Anhang hinzufügen
            db.put_attachment(
                db[doc_id], file_data, filename=attachment_name, content_type="image/jpeg"
            )
            return {"message": f"Anhang {attachment_name} erfolgreich zu Dokument {doc_id} hinzugefügt."}, 201
        except Exception as e:
            return {"error": str(e)}, 500


# Initialisierung der CouchDBHandler-Klasse
couch_handler = CouchDBHandler()

logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a+",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

@app.route('/adddocument', methods=['POST'])
def add_document():
    clip_id = request.form.get('clip_id')
    page = request.form.get('page')
    doc_id = request.form.get('_id')
    token = request.form.get('token')
    file = request.files.get('file')

    # Fehlerprüfung der Eingabe
    if not clip_id or not page or not doc_id:
        return {"error": "Bitte 'clip_id', 'page' und '_id' angeben."}, 400

    if token != SECURITY_TOKEN:
        return {"error": "Ungültiger Security Token!"}, 403

    try:
        # Überprüfung, ob Dokument existiert
        db = couch_handler.server[DATABASE_NAME]
        if doc_id not in db:
            # Dokument erstellen
            db.save({"_id": doc_id, "clip_id": clip_id, "page": page})

        # Attachment verarbeiten
        if file:
            return couch_handler.add_attachment(clip_id, page, doc_id, file)

        return {"message": "Dokument erstellt, ohne ein Attachment hinzuzufügen."}, 201
    except Exception as e:
        logger.error(f"Fehler in /adddocument: {str(e)}")
        return {"error": "Ein interner Serverfehler ist aufgetreten."}, 500


def add_document_attachment(clip_id,page,doc_id,file):

    # Überprüfen, ob alle notwendigen Parameter vorhanden sind
    if not clip_id or not page or not doc_id or file is None:
        return {"error": "Bitte 'clip_id', 'page', '_id' und 'file' angeben."}, 400

    # Aufruf der CouchDB-Handler-Methode
    return couch_handler.add_attachment(clip_id, page, doc_id, file)


@app.route('/get_attachment', methods=['POST'])
def get_attachment():
    # Debug: Alle gesendeten Daten ausgeben
    print("Form-Daten:", request.form)
    print("Datei:", request.files)
    # Daten aus der HTTP-Anfrage abrufen
    request_data = request.get_json()
    clip_id = request_data.get('clip_id')
    page = request_data.get('page')
    token = request_data.get('token')
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    # Überprüfung des Security Tokens
    if token != SECURITY_TOKEN:
        return {"error": "Ungültiger Security Token!"}, 403

    # Überprüfen, ob alle notwendigen Parameter vorhanden sind
    if not clip_id or not page:
        return {"error": "Bitte 'clip_id' und 'page' angeben."}, 400

    # Abrufen des Attachments
    content, attachment_name, status = couch_handler.get_attachment(clip_id, page)

    if status == 200:
        # Antwort mit der heruntergeladenen Datei
        return Response(
            content,
            mimetype="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={attachment_name}"
            }
        )
    else:
        return content, status
@app.route('/get_documents', methods=['POST'])
def get_documents():
    # Daten aus der HTTP-Anfrage abrufen
    request_data = request.get_json()
    clip_id = request_data.get('clip_id')
    token = request_data.get('token')

    # Überprüfung des Security Tokens
    if token not in SECURITY_TOKENS:
        return {"error": "Ungültiger Security Token!"}, 403,

    # Überprüfen, ob 'clip_id' angegeben wurde
    if not clip_id:
        return {"error": "Bitte 'clip_id' angeben."}, 400

    # Aufruf der CouchDBHandler-Methode
    return couch_handler.get_documents_by_clip_id(clip_id)
@app.route('/get_documents_and_attachments', methods=['POST'])
def get_documents_and_attachments():
    # Daten aus der HTTP-Anfrage abrufen
    request_data = request.get_json()
    clip_id = request_data.get('clip_id')
    token = request_data.get('token')

    # Überprüfung des Security Tokens
    if token not in SECURITY_TOKENS:
        return {"error": "Ungültiger Security Token!"}, 403

    # Überprüfen, ob eine clip_id angegeben wurde
    if not clip_id:
        return {"error": "Bitte 'clip_id' angeben."}, 400

    # Sicherstellen, dass der View existiert
    couch_handler.create_clip_id_view()

    # Dokumente und Attachments abrufen
    return couch_handler.get_documents_and_attachments(clip_id)


if __name__ == '__main__':
    app.run(debug=False)