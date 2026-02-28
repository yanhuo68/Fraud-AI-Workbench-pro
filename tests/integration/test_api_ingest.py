import pytest
import io
from unittest.mock import patch, MagicMock

def test_ingest_invalid_file_type(client, auth_headers):
    # Test uploading a non-allowed file type
    response = client.post(
        "/ingest/file",
        files={"file": ("test.exe", b"malicious content", "application/x-msdownload")},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "File type not allowed" in response.json()["detail"]

def test_ingest_file_too_large(client, auth_headers):
    # Mock settings to have a very small max size
    with patch("config.settings.settings.max_file_size_mb", 0.000001): # effectively 1 byte
        response = client.post(
            "/ingest/file",
            files={"file": ("test.csv", b"some,data,here,which,is,longer,than,one,byte", "text/csv")},
            headers=auth_headers
        )
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]

@patch("api.routers.ingest.ingest_uploaded_csv_dynamic")
@patch("rag_sql.graph_utils.create_document_node")
@patch("rag_sql.graph_utils.sync_db_schema_to_graph")
@patch("rag_sql.build_kb_index.build_vectorstore")
def test_ingest_csv_success(
    mock_build_kb, mock_sync, mock_create_node, mock_ingest_csv, 
    client, auth_headers
):
    # Mock return values
    mock_ingest_csv.return_value = ("test_table", 10, ["col1", "col2"])
    
    csv_content = "col1,col2\nval1,val2"
    response = client.post(
        "/ingest/file",
        files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.csv"
    assert data["table_name"] == "test_table"
    
    # Verify processing was triggered
    mock_ingest_csv.assert_called_once()

@patch("rag_sql.graph_utils.create_document_node")
def test_execute_sql_success(mock_create_node, client, auth_headers):
    # We let it hit the real test_db instead of mocking connect, 
    # to avoid breaking get_current_user
    sql_content = "CREATE TABLE test_sql (id INT); INSERT INTO test_sql VALUES (1);"
    response = client.post(
        "/ingest/execute-sql",
        files={"file": ("test.sql", sql_content.encode(), "text/plain")},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "executed successfully" in response.json()["message"]
    mock_create_node.assert_called_once()
