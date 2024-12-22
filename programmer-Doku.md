## **Setup**
### **Systemvoraussetzungen**
- **Python**: Version 3.9 oder höher
- **CouchDB**: Installation und Zugriffskonfiguration
- **Pillow (PIL)**: Für die Bildverarbeitung

### **Python-Abhängigkeiten**
Die benötigten Abhängigkeiten können mit den folgenden Befehlen installiert werden:
``` bash
pip install Flask
pip install couchdb
pip install requests
pip install Pillow
```
### **Konfiguration**
Die Konfiguration erfolgt über die Datei `config.json`. Der Aufbau ist wie folgt:
``` json
{
    "security_tokens": ["my_secure_token_123"],
    "couchdb_server": "http://127.0.0.1:5984/",
    "database_name": "documents_db"
}
```
- **`security_tokens`**: Liste gültiger Sicherheitstokens.
- **`couchdb_server`**: URL der CouchDB-Instanz.
- **`database_name`**: Name der genutzten Datenbank.

## **API-Endpunkte**
Die API bietet folgende REST-Methoden:
### **1. Dokument hinzufügen**
#### URL:
``` http
POST /adddocument
```
#### Beschreibung:
Erstellt ein neues Dokument in der CouchDB und speichert optional ein Bild als Anhang.
#### Anfrage:
- **Header**: `Content-Type: multipart/form-data`
- **Form-Parameter**:
    - `clip_id` (Pflichtfeld): Eindeutige ID des "Clips".
    - `page` (Pflichtfeld): Seiteninformation (z. B. Seitenzahl).
    - `_id` (Pflichtfeld): Eindeutige Dokument-ID.
    - `token` (Pflichtfeld): Sicherheitstoken zur Authentifizierung.
    - `file` (optional): JPEG-Bild, das am Dokument als Anhang gespeichert wird.

#### Antwort:
- **201**: Dokument wurde erfolgreich erstellt.
- **400**: Fehlende Parameter in der Anfrage.
- **403**: Ungültiges Sicherheitstoken.
- **500**: Interner Fehler beim Speichern des Dokuments.

### **2. Dokumente abrufen (nach `clip_id`)**
#### URL:
``` http
POST /get_documents
```
#### Beschreibung:
Liefert alle Dokumente mit einer passenden `clip_id`.
#### Anfrage:
- **Header**: `Content-Type: application/json`
- **Body**:
    - `clip_id` (Pflichtfeld): Eindeutige Clip-ID.
    - `token` (Pflichtfeld): Sicherheitstoken zur Authentifizierung.

#### Antwort:
- **200**: Liste aller zugehörigen Dokumente.
- **403**: Ungültiges Sicherheitstoken.
- **404**: Keine Dokumente für die angegebene `clip_id` gefunden.

### **3. Dokumente und Anhänge abrufen**
#### URL:
``` http
POST /get_documents_and_attachments
```
#### Beschreibung:
Ruft alle Dokumente und deren Anhänge (Base64-codiert) für eine `clip_id` ab.
#### Anfrage:
- **Header**: `Content-Type: application/json`
- **Body**:
    - `clip_id` (Pflichtfeld): Eindeutige Clip-ID.
    - `token` (Pflichtfeld): Sicherheitstoken.

#### Antwort:
- **200**: Liste von Dokumenten mit angehängten Base64-Dateien.
- **403**: Sicherheitstoken ungültig.
- **404**: Keine Dokumente mit der angegebenen `clip_id` gefunden.

### **4. Anhang herunterladen**
#### URL:
``` http
POST /get_attachment
```
#### Beschreibung:
Lädt den Anhang basierend auf `clip_id` und `page` herunter.
#### Anfrage:
- **Header**: `Content-Type: application/json`
- **Body**:
    - `clip_id` (Pflichtfeld): Eindeutige `clip_id`.
    - `page` (Pflichtfeld): Seiteninformation (z.B. Seitenzahl).
    - `token` (Pflichtfeld): Gültiges Sicherheitstoken.

#### Antwort:
- **200**: Der Anhang wird als Datei zurückgegeben.
- **403**: Sicherheitstoken ungültig.
- **404**: Kein Anhang zu den angegebenen Parametern gefunden.

### **CouchDB Views**
Die `clip_id`-basierten Abfragen werden durch folgendes **Design-Dokument** in CouchDB unterstützt:
- **View Name**: `clip_id_index/by_clip_id`
- **Funktion**:
``` javascript
function(doc) {
    if (doc.clip_id) {
        emit(doc.clip_id, { _id: doc._id });
    }
}
```
Diese View indiziert alle Dokumente nach ihrem `clip_id`-Feld, damit schnelle und effiziente Abfragen möglich sind.
## **Wichtige Funktionen**
### **Dokument speichern**
Definiert im `CouchDBHandler` als `add_document`. Erstellt neue Dokumente in der CouchDB-Datenbank.
### **Anhang hinzufügen**
- **Methode**: `add_attachment`
- **Beschreibung**: Fügt ein JPEG-Bild dem angegebenen Dokument hinzu und verkleinert es vor der Speicherung auf **200x200 px**, um Speicher zu sparen.

### **Dokumente abrufen**
- **Methode**: `get_documents_by_clip_id`
- **Beschreibung**: Ruft Dokumente mit übereinstimmender `clip_id` ab.

### **Anhänge anzeigen**
- **Methode**: `get_documents_and_attachments`
- **Beschreibung**: Liefert Dokumente und Base64-Informationen ihrer Anhänge.

## **Stress-Test**
Der Stress-Test (`stress_test_utils.py`) kann benutzt werden, um die API unter hoher Last zu testen. Dazu werden parallele Threads verwendet, um die gleichzeitige Nutzung zu simulieren.
### **Test-Einstellungen**
- **Endpunkte**: `/adddocument` oder `/get_documents_and_attachments`
- **Konfigurierbare Parameter**:
    - **`CONCURRENT_REQUESTS`**: Anzahl gleichzeitiger Anfragen (z. B. 50, 1000).
    - Größe der Anhänge (`size_kb`).

### **Tests ausführen**
1. Starte den Flask-Server:
``` bash
   python main.py
```
1. Führe den Stress-Test aus:
``` bash
   python stress_test_utils.py
```
Das Skript gibt aus, wie viele Anfragen erfolgreich oder fehlgeschlagen sind.
## **Fehlerbehebung**
### **Sicherheitstoken ungültig (403)**
Stelle sicher, dass das verwendete Token in der Datei `config.json` definiert ist.
### **Fehlende Dokumente (404)**
Verwende die Funktion `/adddocument`, um sicherzustellen, dass entsprechende Dokumente erstellt wurden.
### **CouchDB-Verbindungsprobleme**
- Überprüfe, ob CouchDB läuft (`http://127.0.0.1:5984` lädt im Browser).
- Verifiziere die Konfiguration (`DATABASE_NAME`, `COUCHDB_SERVER`).
