## **Systemanforderungen**
### **Hardware-Voraussetzungen**
- **CPU**: Mindestens 2 Cores empfohlen
- **RAM**: Minimum 2 GB (empfohlen: 4 GB für parallele Lasttests)
- **Speicherplatz**: Hängt von der Anzahl und Größe der Dokumente und Anhänge ab. Reserve von mindestens 10 GB empfohlen.

### **Software-Voraussetzungen**
1. **Betriebssystem**:
    - Linux (empfohlen: Ubuntu 20.04/22.04)
    - macOS
    - Windows Server

2. **Python**: Version 3.9 oder höher
3. **CouchDB**: Version 3.x oder höher. Stelle sicher, dass CouchDB vollständig installiert und lauffähig ist.
4. **Weitere Abhängigkeiten**:
    - Libraries: Flask, couchdb, requests, Pillow (PIL)
    - Python-Paketmanager: `pip`

## **Netzwerkanforderungen**
1. **Portfreigaben**:
    - Flask API Standardport: **5000**
    - CouchDB Standardport: **5984**

2. **IP-Adresse**:
    - Der Flask-Server und CouchDB sollten idealerweise auf statischen IP-Adressen (oder localhost) laufen.

3. **Authentifizierung**:
    - CouchDB benötigt ein Admin-Login für sichere Verbindungen.

4. **Sicherheitsmaßnahmen**:
    - **Firewall**: Nur Server und Clients, die Zugriff benötigen, dürfen Verbindungen öffnen.
    - **HTTPS-Absicherung**: Bei externem Zugriff ist die API in eine HTTPS-Umgebung einzubinden.

## **Installationsanleitung**
### **1. CouchDB installieren**
Für Ubuntu-basierte Systeme:
``` bash
sudo apt update
sudo apt install couchdb
```
Folge der Installationsanleitung, um CouchDB im **Standalone-Modus** oder **Cluster-Modus** einzurichten.
Nach der Installation:
1. Öffne den CouchDB-Admin-Bereich unter `http://127.0.0.1:5984/_utils/`.
2. Erstelle die Datenbank, die in der JSON-Konfiguration angegeben wird (z. B. `documents_db`):
    - **Datenbankname**: `documents_db`

#### **Einstellungen nach Installation**:
- Bearbeite die Konfigurationsdatei von CouchDB:
``` bash
  sudo nano /etc/couchdb/local.ini
```
- **Wichtige Parameter**:
``` ini
  [httpd]
  bind_address = 0.0.0.0     ; Soll auf allen Schnittstellen verfügbar sein (nur bei Bedarf)

  [admins]
  admin = passwort            ; Optional: Admin-Benutzer hinzufügen

  [couch_httpd_auth]
  secret = <geheimer_schlüssel>
  timeout = 600
```
Teste CouchDB mithilfe von:
``` bash
curl http://127.0.0.1:5984/
```
### **2. Python-Umgebung vorbereiten**
1. **Virtuelle Umgebung erstellen**:
``` bash
   python3 -m venv venv
   source venv/bin/activate   # Unter Windows: .\venv\Scripts\activate
```
1. **Abhängigkeiten installieren**:
``` bash
   pip install Flask couchdb requests Pillow
```
### **3. Konfigurationsdatei anpassen**
In der `config.json` stehen alle benötigten Parameter:
``` json
{
    "security_tokens": ["my_secure_token_123"],
    "couchdb_server": "http://127.0.0.1:5984/",
    "database_name": "documents_db"
}
```
- **`security_tokens`**: Zugangsschlüssel, die von der API benötigt werden. Systemintegratoren können mehrere Schlüssel hinterlegen.
- **`couchdb_server`**: Die URL der CouchDB-Instanz (ändert sich ggf. je nach Hostname oder IP).
- **`database_name`**: Name der Datenbank. Stelle sicher, dass der korrekte Name in CouchDB erstellt ist.

### **4. Flask-Server starten**
Führe den Flask-Server mit folgendem Befehl aus:
``` bash
python main.py
```
#### Serveroptionen:
- Standardmäßig startet der Server unter **[http://127.0.0.1:5000]()**.
- Falls der Server auf allen IPs lauschen soll:
``` bash
  python main.py --host 0.0.0.0 --port 5000
```
## **Wartung**
### **Log- und Fehlerdiagnosen**
- **Flask-Logs**:
    - Fehler und Anfragen werden in `app.log` protokolliert.
    - Speicherort: Im Root-Verzeichnis der Anwendung.

- **CouchDB-Logs**:
    - Linux:
``` bash
    tail -f /var/log/couchdb/couch.log
```
- Zeigt Verbindungs-, Schreib- und Leseprobleme an.

### **Sicherheitsmaßnahmen**
1. **Token-Verwaltung**:
    - `config.json` ständig aktualisieren. Unerlaubte Token entfernen.

2. **Datenbank-Zugriff**:
    - Kein anonymer Zugriff auf CouchDB zulassen. Nutze CouchDB-Berechtigungen für den Benutzer der Anwendung.
    - Für sensitive Daten sollte CouchDB TLS/SSL (Port 6984) verwenden:
        - Anleitung: [CouchDB HTTPS einrichten]().

3. **Backup der Datenbank**:
    - Führe regelmäßige Dumps der CouchDB-Datenbank durch:
``` bash
     curl http://127.0.0.1:5984/documents_db/_all_docs > backup.json
```
1. **Server-Härtung**:
    - Verwende Firewalls und sichere Zugriffssteuerungen (z. B. `iptables`).
    - Richtlinien für API-Zugriff nur von bekannten IP-Adressen durchsetzen.

### **Datenbankwartung**
1. **Autorisierung bestätigen**:
    - CouchDB benötigt einen Admin. Die Datei `/etc/couchdb/local.ini` enthält Benutzerinformationen.

2. **Index-Verwaltung (Views)**:
    - Stelle sicher, dass der View `clip_id_index` existiert, der durch die Anwendung erstellt wird:
        - Abrufen aller Views:
``` bash
       curl http://127.0.0.1:5984/documents_db/_design/clip_id_index
```
- Bei Problemen (fehlender View) kann die Anwendung (Flask) den View automatisch durch **`create_clip_id_view`** erstellen.

1. **Leistungsoptimierung**:
    - Zum Optimieren von CouchDB-Abläufen:
        - Führe **Compaction** durch:
``` bash
       curl -X POST http://127.0.0.1:5984/documents_db/_compact
```
### **Fehlerbehebung**

| Problem | Ursache | Lösung |
| --- | --- | --- |
| Flask-Server startet nicht | Abhängigkeiten fehlen | Installiere die Anforderungen mit `pip install Flask couchdb requests Pillow`. |
| CouchDB-Verbindungsfehler | CouchDB nicht gestartet | Stelle sicher, dass CouchDB läuft: `sudo systemctl status couchdb`. |
| API gibt "Ungültiger Security Token" zurück | Token fehlt oder nicht gültig | Überprüfen, ob korrekter Token in `config.json` angegeben wurde. |
| Keine Dokumente gefunden | View nicht erstellt | Stelle sicher, dass der View `clip_id_index` existiert und Daten korrekt in der CouchDB liegen. |
| CouchDB-Dokumente können nicht gespeichert werden | Mangelnde Schreibrechte für den Benutzer | Überprüfen und aktualisieren der CouchDB-Benutzerrechte. |
## **Nützliche Befehle**
### Flask-Server testen:
``` bash
curl -X POST http://127.0.0.1:5000/adddocument -F "clip_id=test_clip" -F "page=1" -F "_id=test_doc" -F "token=my_secure_token_123"
```
### CouchDB-Dienst starten:
``` bash
sudo systemctl start couchdb
```
### CouchDB-Datenbank-Dump erstellen:
``` bash
curl http://127.0.0.1:5984/documents_db/_all_docs?include_docs=true > backup.json
```
