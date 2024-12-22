# README
## **Thumbnail Manager**
Der **Thumbnail Manager** ist eine RESTful-Webanwendung, die mit **Flask** entwickelt wurde und es ermöglicht, Thumbnails für Dokumente effizient zu verwalten. Die Anwendung verbindet sich mit **CouchDB**, um Dokumente und deren Anhänge zu speichern und abzurufen.
Die Hauptfunktionalität besteht darin, **JPEG-Bilder als Thumbnails hochzuladen**, die automatisch auf eine Größe von **200x200 Pixel** verkleinert werden, und sie mit den entsprechenden Dokumenten zu verknüpfen.
## **Inhaltsverzeichnis**
1. [Features]()
2. [Technische Anforderungen]()
3. [Installation]()
4. [Konfiguration]()
5. [API-Endpunkte]()
6. [Fehlerbehebung]()
7. [Lizenz]()

## **Features**
- **Thumbnail-Generierung**: Automatische Erstellung von Thumbnails (200x200 Pixel) aus hochgeladenen JPEG-Bildern.
- **Dokumenten-Management**: Hinzufügen, Verknüpfen und Abrufen von Dokumenten und deren Anhängen in einer CouchDB-Datenbank.
- **Integration von CouchDB Views**: Organisation von Daten über **Views** nach Clip-ID für effiziente Abfragen.
- **Dateianhang-Management**: Speicherung und Verwaltung von Anhängen (z. B. Bildern) direkt in der Datenbank.
- **Sicherheit**: Zugriff auf Endpunkte wird durch **Security-Tokens** geschützt.

## **Technische Anforderungen**
### **Software**
- **Python**: Version 3.9 oder höher.
- **CouchDB**: Version 3.x oder höher.
- **Abhängigkeiten**: Flask, CouchDB-Python, Pillow u.a.

### **Netzwerk**
- API läuft standardmäßig auf `port 5000`.
- Verbindungsport für CouchDB wird in `config.json` konfiguriert (Standard: `5984`).

### **Hardware**
- Mindestens 2 CPU-Kerne.
- 2 GB RAM (empfohlen 4 GB).
- Freier Speicherplatz: mindestens 10 GB.

## **Installation**
### **1. Repository klonen**
``` bash
git clone <repository-url>
cd <repository-name>
```
### **2. Virtuelle Umgebung erstellen**
Erstelle eine virtuelle Python-Umgebung und installiere alle Abhängigkeiten:
``` bash
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```
### **3. CouchDB einrichten**
- Installiere und starte **CouchDB**.
- Konfiguriere die CouchDB-Datenbank und den Benutzerzugang entsprechend der [Konfiguration]().

### **4. Anwendung starten**
``` bash
python main.py
```
Die Anwendung ist unter `http://127.0.0.1:5000` verfügbar.
## **Konfiguration**
Alle Konfigurationseinstellungen werden in der Datei `config.json` gespeichert.
### **Beispiel: `config.json`**
``` json
{
  "security_tokens": ["my_secure_token_123"],
  "couchdb_server": "http://localhost:5984/",
  "database_name": "thumbnails_db"
}
```
### **Einstellungen:**

| Konfigurationsfeld | Beschreibung |
| --- | --- |
| **security_tokens** | Liste der API-Sicherheitstoken |
| **couchdb_server** | URL des CouchDB-Servers (inkl. Portangabe) |
| **database_name** | Name der CouchDB-Datenbank |
## **API-Endpunkte**
### **1. Dokument hinzufügen**
- **URL**: `/adddocument`
- **Methode**: `POST`
- **Beschreibung**: Erstellt ein neues Dokument und speichert optional ein Bild als Thumbnail.

**Parameter (Form-Data):** | Parameter | Typ | Erforderlich | Beschreibung | |-------------|-----------|--------------|--------------------------------| | `clip_id` | String | Ja | Eindeutige ID des Clips | | `page` | Integer | Ja | Seitennummer | | `_id` | String | Ja | Eindeutige Dokument-ID | | `file` | File | Nein | JPEG-Bild | | `token` | String | Ja | API-Security-Token |
**Antwort:**
``` json
{
  "message": "Dokument erstellt, ohne ein Attachment hinzuzufügen."
}
```
### **2. Thumbnails für eine Clip-ID abrufen**
- **URL**: `/get_documents_and_attachments`
- **Methode**: `POST`
- **Beschreibung**: Holt alle Dokumente und deren zugehörige Anhänge für eine bestimmte Clip-ID.

**Parameter (JSON):** | Parameter | Typ | Erforderlich | Beschreibung | |-------------|-----------|--------------|--------------------------------| | `clip_id` | String | Ja | Eindeutige ID des Clips | | `token` | String | Ja | API-Security-Token |
**Antwort:**
``` json
{
  "documents": [
    {
      "document_id": "id123",
      "clip_id": "clip123",
      "attachments": [
        {
          "name": "clip123_page1.jpg",
          "content_type": "image/jpeg",
          "data": "<Base64-kodierte Daten>"
        }
      ]
    }
  ]
}
```
### **3. Anhänge als Datei herunterladen**
- **URL**: `/get_attachment`
- **Methode**: `POST`
- **Beschreibung**: Ruft einen Anhang basierend auf Clip-ID und Seitennummer ab und gibt die Datei zurück.

**Parameter (JSON):** | Parameter | Typ | Erforderlich | Beschreibung | |-------------|-----------|--------------|----------------------------| | `clip_id` | String | Ja | Eindeutige ID des Clips | | `page` | Integer | Ja | Seitennummer | | `token` | String | Ja | API-Security-Token |
**Antwort:**
Die Datei wird als **Download** bereitgestellt.
## **Fehlerbehebung**

| Problem | Ursache | Lösung |
| --- | --- | --- |
| **Server startet nicht** | Fehlende `config.json` | Datei erstellen und konfigurieren. |
| **CouchDB nicht erreichbar** | Falsche CouchDB-URL | Prüfe `couchdb_server` in `config.json`. |
| **Token abgelehnt** | Ungültiges Token | Sicherstellen, dass das Token korrekt ist. |
| **Bild nicht akzeptiert** | Bildformat nicht JPEG | Lade ein **JPEG-Bild** hoch. |
## **Lizenz:**

## **Open Thumbnail Python Edition © 2024 by Luis Schumacher is licensed under CC BY-NC-SA 4.0**

| Sie dürfen:                                                                               | Unter folgenden Bedingungen:                                                                            |
|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| Teilen (das Material in jedwedem Format oder Medium vervielfältigen und weiterverbreiten) | Namensnennung, Nicht kommerziell, Weitergabe unter gleichen Bedingungen, Keine weiteren Einschränkungen |
| Bearbeiten (das Material remixen, verändern und darauf aufbauen)                          | Namensnennung, Nicht kommerziell, Weitergabe unter gleichen Bedingungen, Keine weiteren Einschränkungen |

Jegliche kommerzielle Nutzung ohne die ausdrückliche Einwilligung des Autors ist untersagt.

### _**Dieses Programm wird in der Hoffnung verbreitet, dass es nützlich sein wird, jedoch OHNE JEDE GEWÄHRLEISTUNG; sogar ohne die implizite Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.**_