import os
import random
import string
import time
import requests
from concurrent.futures import ThreadPoolExecutor
import warnings
from tempfile import NamedTemporaryFile

from PIL import Image, ImageDraw


# REST-API-URL und Security-Token konfigurieren
REST_API_URL = "http://127.0.0.1:5000/adddocument"
REST_API_GET_DOCS_URL = "http://127.0.0.1:5000/get_documents_and_attachments"
SECURITY_TOKEN = "my_secure_token_123"

# Anzahl der gleichzeitigen Anfragen
CONCURRENT_REQUESTS = 100000


# Funktion zur Generierung einer Datei mit einer Mindestgröße von 15 KB


def generate_random_attachment(size_kb=15):
    size_bytes = size_kb * 1024
    image_size = (200, 200)  # Beispielgröße für Dummy-Bilder (200x200 px)

    # Dummy-Bild erstellen
    image = Image.new("RGB", image_size, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Test", fill=(255, 255, 255))  # Dummy-Text hinzufügen

    # Temporäre Datei erstellen
    temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
    image.save(temp_file, format="JPEG")

    # Überprüfen, ob die Datei groß genug ist, ansonsten auffüllen mit Dummy-Daten
    file_size = os.path.getsize(temp_file.name)
    if file_size < size_bytes:
        with open(temp_file.name, "ab") as f:
            f.write(b"\0" * (size_bytes - file_size))

    return temp_file.name


# Funktion zur Durchführung einer Anfrage
def send_request(request_id):
    try:
        # Zufällige Daten generieren
        clip_id = f"clip_{request_id}"
        page = str(random.randint(1, 100))
        doc_id = f"doc_{request_id}"

        # Zufällige Datei erstellen (mind. 15 KB)
        attachment_file = generate_random_attachment()

        # Daten für die Anfrage vorbereiten
        files = {
            "file": (attachment_file, open(attachment_file, "rb"), "image/jpeg")
        }
        data = {
            "clip_id": clip_id,
            "page": page,
            "_id": doc_id,
            "token": SECURITY_TOKEN
        }
        time.sleep(0.01)
        # POST-Anfrage senden
        response = requests.post(REST_API_URL, data=data, files=files)
        time.sleep(0.01)
        # Temporäre Datei entfernen
        os.remove(attachment_file)

        # Ergebnis der Anfrage ausgeben
        if response.status_code == 201:
            print(f"Request {request_id} succeeded: {response.json()}")
        else:
            print(f"Request {request_id} failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request {request_id} encountered an error: {e}")


# Hauptfunktion für den Stresstest
def stress_test():
    start_time = time.time()

    # ThreadPool für parallele Anfragen erstellen
    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(send_request, request_id) for request_id in range(CONCURRENT_REQUESTS)]

        # Auf Abschluss aller Anfragen warten
        for future in futures:
            future.result()

    end_time = time.time()
    print(f"Stress test finished in {end_time - start_time:.2f} seconds")
# Funktion zur Durchführung einer Abfrage-Anfrage
def send_get_request(request_id):
    try:
        # Zufällige clip_id generieren basierend auf der Anfrage-ID
        clip_id = f"clip_{request_id}"

        # Daten für die Anfrage vorbereiten
        data = {
            "clip_id": clip_id,
            "token": SECURITY_TOKEN
        }

        # POST-Anfrage senden
        response = requests.post(REST_API_GET_DOCS_URL, json=data)

        # Ergebnis ausgeben
        if response.status_code == 200:
            print(f"Request {request_id} succeeded: {response.json()}")
        else:
            print(f"Request {request_id} failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request {request_id} encountered an error: {e}")


# Hauptfunktion für den Stress-Test von GET-Anfragen
def stress_test_get_documents():
    start_time = time.time()

    # ThreadPool für parallele Anfragen erstellen
    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(send_get_request, request_id) for request_id in range(CONCURRENT_REQUESTS)]

        # Auf Abschluss aller Anfragen warten
        for future in futures:
            future.result()

    end_time = time.time()
    print(f"Stress test for GET requests finished in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
   # stress_test()
    stress_test_get_documents()