from fastapi.testclient import TestClient
from main import app
from app.core.security import verify_admin_user
from unittest.mock import patch, MagicMock

client = TestClient(app)

async def override_verify_admin_user():
    return {"id": "test-admin-id", "email": "admin@nutrablue.cl"}

def test_sync_products_sheets_success():
    # Override authentication dependency for this test
    app.dependency_overrides[verify_admin_user] = override_verify_admin_user
    
    mock_csv = "Nombre,Precio,Stock,Categoría,Imagen,Beneficios,Certificaciones,Ficha\n" \
               "Super Beetle Protein,19990,100,Proteínas,http://img.jpg,Alto en Hierro;Sostenible,Orgánico;SAG,https://docs.google.com/document/123\n"

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_csv
        mock_get.return_value = mock_response

        response = client.post("/admin/products/sync-sheets", json={"csv_url": "http://fake-sheet.csv"})
        
        # Verify status code
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["summary"]["created"] + data["summary"]["updated"] == 1
        assert len(data["summary"]["errors"]) == 0

    # Clean overrides
    app.dependency_overrides.clear()

def test_sync_products_sheets_validation_error():
    app.dependency_overrides[verify_admin_user] = override_verify_admin_user
    
    # Bad stock (non-numeric string)
    mock_csv = "Nombre,Precio,Stock,Categoría,Imagen,Beneficios,Certificaciones,Ficha\n" \
               "Bad Stock Product,19990,not-a-number,Proteínas,,,,\n"

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_csv
        mock_get.return_value = mock_response

        response = client.post("/admin/products/sync-sheets", json={"csv_url": "http://fake-sheet.csv"})
        
        assert response.status_code == 200
        data = response.json()
        # Even if one product fails, it returns success=True if at least some succeed, but here it's 0/1 success.
        assert len(data["summary"]["errors"]) == 1
        assert data["summary"]["errors"][0]["product"] == "Bad Stock Product"

    app.dependency_overrides.clear()
