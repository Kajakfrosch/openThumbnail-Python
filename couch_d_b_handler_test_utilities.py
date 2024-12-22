from unittest.mock import patch, MagicMock
import pytest
from main import CouchDBHandler, DATABASE_NAME, app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()
def test_get_documents_by_clip_id():
    # Mock CouchDB-Verbindung
    handler = CouchDBHandler()
    mock_db = MagicMock()
    handler.server[DATABASE_NAME] = mock_db

    # View-Ergebnisse simulieren
    mock_db.view.return_value = [{"_id": "test_doc"}]

    result, status = handler.get_documents_by_clip_id("test_clip")
    assert status == 200
    assert "documents" in result
    assert len(result["documents"]) == 1