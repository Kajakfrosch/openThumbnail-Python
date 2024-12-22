import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

# Nur Nutzbar wenn Couchdb Verfügbar ist
#def test_add_document_success(client):
#    response = client.post('/adddocument', data={
#        'clip_id': 'test_clip',
#        'page': '1',
#        '_id': 'test_doc_id',
#        'token': 'my_secure_token_123'
#    })

    assert response.status_code == 201
    assert "Dokument erstellt" in response.get_json()["message"]


def test_add_document_without_token(client):
    response = client.post('/adddocument', data={
        'clip_id': 'test_clip',
        'page': '1',
        '_id': 'test_doc_id'
    })
    assert response.status_code == 403
    assert "Ungültiger Security Token" in response.get_json()["error"]


def test_add_document_with_invalid_token(client):
    response = client.post('/adddocument', data={
        'clip_id': 'test_clip',
        'page': '1',
        '_id': 'test_doc_id',
        'token': 'wrong_token'
    })
    assert response.status_code == 403
    assert "Ungültiger Security Token" in response.get_json()["error"]
# Nur Nutzbar wenn Couchdb Verfügbar ist
#def test_get_documents_success(client):
#    response = client.post('/get_documents', json={
#        'clip_id': 'test_clip',
#        'token': 'my_secure_token_123'
#    })
#    assert response.status_code == 200
#    assert "documents" in response.get_json()


def test_get_documents_invalid_token(client):
    response = client.post('/get_documents', json={
        'clip_id': 'test_clip',
        'token': 'wrong_token'
    })
    assert response.status_code == 403
    assert "Ungültiger Security Token" in response.get_json()["error"]


def test_get_documents_no_clip_id(client):
    response = client.post('/get_documents', json={
        'token': 'my_secure_token_123'
    })
    assert response.status_code == 400
    assert "Bitte 'clip_id' angeben." in response.get_json()["error"]
# Nur Nutzbar wenn Couchdb Verfügbar ist
#def test_get_documents_and_attachments_success(client):
#    response = client.post('/get_documents_and_attachments', json={
#        'clip_id': 'test_clip',
#        'token': 'my_secure_token_123'
#    })
#    assert response.status_code == 200
#    assert "documents" in response.get_json()


def test_get_documents_and_attachments_invalid_token(client):
    response = client.post('/get_documents_and_attachments', json={
        'clip_id': 'test_clip',
        'token': 'wrong_token'
    })
    assert response.status_code == 403
    assert "Ungültiger Security Token" in response.get_json()["error"]






def test_get_attachment_invalid_token(client):
    response = client.post('/get_attachment', json={
        'clip_id': 'test_clip',
        'page': '1',
        'token': 'wrong_token'
    })
    assert response.status_code == 403
    assert "Ungültiger Security Token" in response.get_json()["error"]

