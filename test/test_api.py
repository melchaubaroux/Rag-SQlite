import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, '../RAG-Sqlites')

# On importe ton app FastAPI
from API.api_rag import app

# --- FIXTURE : CLIENT DE TEST ---
@pytest.fixture
def client():
    return TestClient(app)


# --- TEST PAGE DE LOGIN ---
def test_login_page(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "login" in r.text.lower()


# --- TEST LOGIN ÉCHEC ---
def test_login_fail(client):
    r = client.post("/login", data={"username": "x", "password": "y"})
    assert r.status_code == 200
    assert "incorrect" in r.text.lower()


# --- TEST LOGIN SUCCÈS ---
def test_login_success(client):
    r = client.post("/login", data={"username": "admin", "password": "admin"},follow_redirects=False)
    assert r.status_code == 303
    assert "auth" in r.cookies
    assert r.cookies["auth"] == "ok"


# --- TEST ACCÈS PROTÉGÉ SANS COOKIE ---
def test_home_unauthorized(client):
    r = client.get("/",follow_redirects=False)
    assert "auth" not  in r.cookies
    # Redirection vers /login
    assert r.status_code == 303


# --- TEST ACCÈS PROTÉGÉ AVEC COOKIE ---
def test_home_authorized(client):
    r = client.get("/", cookies={"auth": "ok"})
    assert r.status_code == 200


# --- TEST LISTE DES TABLES ---
def test_liste_tables(client):
    r = client.get("/liste tables")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# --- MOCK UPLOAD PDF ---
def test_upload_pdf(client, tmp_path, monkeypatch):
    # Création d’un faux PDF
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 FAKE")

    # Mock conversion PDF → Markdown
    def mock_to_md(path):
        return "# fake markdown"

    monkeypatch.setattr("pymupdf4llm.to_markdown", mock_to_md)

    # Mock insertion en DB
    def mock_insert(model, md):
        return True

    monkeypatch.setattr("API.api_rag.insert_document_in_markdown_format", mock_insert)

    # Envoi du faux PDF
    with fake_pdf.open("rb") as f:
        r = client.post(
            "/upload",
            files={"pdf": ("fake.pdf", f, "application/pdf")}
        )

    assert r.status_code == 200
    assert "uploadé" in r.text.lower()


# --- TEST /request (search vectoriel) ---
def test_vector_request(client, monkeypatch):

    # Mock embedding
    class FakeModel:
        def encode(self, x):
            return [0.1] * 512

    monkeypatch.setattr("API.api_rag.model", FakeModel())

    # Mock recherche vectorielle
    def fake_search(cursor, query, limit):
        return [{"score": 0.99, "content": "fake"}]

    monkeypatch.setattr("API.api_rag.search_in_vbase", fake_search)

    r = client.get("/request?request=test&limit=3")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert r.json()[0]["content"] == "fake"
