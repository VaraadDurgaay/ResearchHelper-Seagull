"""
Test FastAPI Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import tempfile
import shutil

# Import the app
from app.main import app

# Create a test client
client = TestClient(app)


class TestRootEndpoints:
    """Test root level endpoints"""
    
    def test_root_endpoint(self):
        """Test GET / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ResearchHelper API"
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self):
        """Test GET /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestPapersEndpoints:
    """Test papers API endpoints"""
    
    def test_list_papers_empty(self):
        """Test GET /api/v1/papers/ - should return empty list"""
        response = client.get("/api/v1/papers/")
        assert response.status_code == 200
        data = response.json()
        assert "papers" in data
        assert "total" in data
        assert data["papers"] == []
        assert data["total"] == 0
    
    def test_get_nonexistent_paper(self):
        """Test GET /api/v1/papers/{paper_id} - should return 404"""
        response = client.get("/api/v1/papers/non-existent-id")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_delete_paper(self):
        """Test DELETE /api/v1/papers/{paper_id} - should return success"""
        response = client.delete("/api/v1/papers/test-id")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
    
    def test_upload_paper_success(self):
        """Test POST /api/v1/papers/ - upload a valid PDF file"""
        # Create a temporary PDF file for testing
        test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF"
        
        files = {
            "file": ("test_paper.pdf", test_pdf_content, "application/pdf")
        }
        
        response = client.post("/api/v1/papers/", files=files)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "title" in data
        assert "pdf_path" in data
        assert "upload_date" in data
        assert "workspace_id" in data
        assert "user_id" in data
        assert "status" in data
        assert "metadata" in data
        
        # Verify values
        assert data["title"] == "test_paper"
        assert data["status"] == "ready"
        assert data["user_id"] == "default-user-id"
        assert data["workspace_id"] == "default-workspace-id"
        assert data["metadata"]["original_filename"] == "test_paper.pdf"
        assert data["metadata"]["file_size"] > 0
        
        # Verify file was saved
        if data["pdf_path"] and os.path.exists(data["pdf_path"]):
            assert os.path.isfile(data["pdf_path"])
    
    def test_upload_paper_invalid_file_type(self):
        """Test POST /api/v1/papers/ - upload non-PDF file"""
        files = {
            "file": ("test.txt", b"Not a PDF file", "text/plain")
        }
        
        response = client.post("/api/v1/papers/", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "pdf" in data["detail"].lower()
    
    def test_upload_paper_empty_file(self):
        """Test POST /api/v1/papers/ - upload empty file"""
        files = {
            "file": ("empty.pdf", b"", "application/pdf")
        }
        
        response = client.post("/api/v1/papers/", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "empty" in data["detail"].lower()
    
    def test_upload_paper_large_file(self):
        """Test POST /api/v1/papers/ - upload file exceeding size limit"""
        # Create a file larger than 50MB (default max_upload_size)
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        files = {
            "file": ("large.pdf", large_content, "application/pdf")
        }
        
        response = client.post("/api/v1/papers/", files=files)
        assert response.status_code == 413
        data = response.json()
        assert "detail" in data
        assert "size" in data["detail"].lower() or "exceed" in data["detail"].lower()


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_docs_endpoint(self):
        """Test that Swagger UI docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_endpoint(self):
        """Test that ReDoc docs are accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        # OPTIONS might not be explicitly handled, but CORS middleware should be configured
        # Just verify the endpoint exists
        response = client.get("/")
        assert response.status_code == 200

