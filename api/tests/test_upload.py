"""Tests for the receipt upload endpoint."""

import io
import uuid


class TestUploadSuccess:
    """Tests for successful file uploads."""

    def test_upload_valid_png(self, client, sample_png):
        """Test uploading a valid PNG file returns 200."""
        filename, file_obj, content_type = sample_png
        response = client.post(
            "/receipts/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        assert response.status_code == 200
        data = response.json()
        assert "receipt_id" in data
        assert data["status"] == "pending"

    def test_upload_valid_jpeg(self, client, sample_jpeg):
        """Test uploading a valid JPEG file returns 200."""
        filename, file_obj, content_type = sample_jpeg
        response = client.post(
            "/receipts/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        assert response.status_code == 200
        data = response.json()
        assert "receipt_id" in data
        assert data["status"] == "pending"

    def test_upload_valid_pdf(self, client, sample_pdf):
        """Test uploading a valid PDF file returns 200."""
        filename, file_obj, content_type = sample_pdf
        response = client.post(
            "/receipts/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        assert response.status_code == 200
        data = response.json()
        assert "receipt_id" in data
        assert data["status"] == "pending"

    def test_upload_response_format(self, client, sample_png):
        """Test response matches expected UploadResponse model."""
        filename, file_obj, content_type = sample_png
        response = client.post(
            "/receipts/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "receipt_id" in data
        assert "status" in data
        assert "message" in data

        # Verify receipt_id is a valid UUID
        uuid.UUID(data["receipt_id"])

        # Verify status is "pending"
        assert data["status"] == "pending"

        # Verify message is present and non-empty
        assert len(data["message"]) > 0


class TestUploadValidation:
    """Tests for file type validation errors."""

    def test_upload_invalid_file_type_text(self, client, sample_text_file):
        """Test uploading a text file returns 400."""
        filename, file_obj, content_type = sample_text_file
        response = client.post(
            "/receipts/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

    def test_upload_unsupported_mime_type_gif(self, client):
        """Test uploading a GIF file returns 400."""
        gif_bytes = b"GIF89a\x01\x00\x01\x00\x00\x00\x00;"
        response = client.post(
            "/receipts/upload",
            files={"file": ("test.gif", io.BytesIO(gif_bytes), "image/gif")}
        )
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

    def test_upload_missing_file(self, client):
        """Test uploading without a file returns 422."""
        response = client.post("/receipts/upload")
        assert response.status_code == 422


class TestUploadSizeValidation:
    """Tests for file size validation."""

    def test_upload_file_too_large(self, client, large_file):
        """Test uploading a file larger than 10MB returns 413."""
        filename, file_obj, content_type = large_file
        response = client.post(
            "/receipts/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        assert response.status_code == 413
        assert "10MB" in response.json()["detail"]

    def test_upload_file_at_size_limit(self, client):
        """Test uploading a file exactly at 10MB succeeds."""
        size = 10 * 1024 * 1024  # Exactly 10MB
        content = b"x" * size
        response = client.post(
            "/receipts/upload",
            files={"file": ("test.png", io.BytesIO(content), "image/png")}
        )
        assert response.status_code == 200


class TestUploadEdgeCases:
    """Tests for edge cases."""

    def test_upload_empty_file(self, client):
        """Test uploading an empty file."""
        response = client.post(
            "/receipts/upload",
            files={"file": ("empty.png", io.BytesIO(b""), "image/png")}
        )
        # Empty file should still be accepted (validation happens later)
        assert response.status_code == 200

    def test_upload_generates_unique_ids(self, client, sample_png):
        """Test that each upload generates a unique receipt ID."""
        filename, file_obj, content_type = sample_png

        # First upload
        response1 = client.post(
            "/receipts/upload",
            files={"file": (filename, io.BytesIO(file_obj.read()), content_type)}
        )
        file_obj.seek(0)

        # Second upload
        response2 = client.post(
            "/receipts/upload",
            files={"file": (filename, io.BytesIO(file_obj.read()), content_type)}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["receipt_id"] != response2.json()["receipt_id"]


class TestMultipleUploadsSequential:
    """Tests simulating multiple sequential uploads (as done by frontend)."""

    def test_sequential_uploads_multiple_files(self, client, sample_png, sample_jpeg, sample_pdf):
        """Test uploading multiple files sequentially returns unique IDs and all succeed."""
        files_to_upload = [sample_png, sample_jpeg, sample_pdf]
        receipt_ids = []

        for filename, file_obj, content_type in files_to_upload:
            response = client.post(
                "/receipts/upload",
                files={"file": (filename, io.BytesIO(file_obj.read()), content_type)}
            )
            assert response.status_code == 200
            data = response.json()
            assert "receipt_id" in data
            assert data["status"] == "pending"
            receipt_ids.append(data["receipt_id"])

        # Verify all IDs are unique
        assert len(receipt_ids) == len(set(receipt_ids))

    def test_sequential_uploads_with_one_failure(self, client, sample_png, sample_text_file):
        """Test that one failed upload doesn't affect subsequent uploads."""
        # First upload (should succeed)
        filename1, file_obj1, content_type1 = sample_png
        response1 = client.post(
            "/receipts/upload",
            files={"file": (filename1, io.BytesIO(file_obj1.read()), content_type1)}
        )
        assert response1.status_code == 200

        # Second upload (should fail - invalid file type)
        filename2, file_obj2, content_type2 = sample_text_file
        response2 = client.post(
            "/receipts/upload",
            files={"file": (filename2, io.BytesIO(file_obj2.read()), content_type2)}
        )
        assert response2.status_code == 400

        # Third upload (should succeed - verify previous failure didn't affect server)
        file_obj1.seek(0)
        response3 = client.post(
            "/receipts/upload",
            files={"file": (filename1, io.BytesIO(file_obj1.read()), content_type1)}
        )
        assert response3.status_code == 200

        # Verify the two successful uploads have different IDs
        assert response1.json()["receipt_id"] != response3.json()["receipt_id"]

    def test_rapid_sequential_uploads(self, client, sample_png):
        """Test rapid sequential uploads (simulating fast frontend queue processing)."""
        filename, file_obj, content_type = sample_png
        num_uploads = 5
        receipt_ids = []

        for i in range(num_uploads):
            file_obj.seek(0)
            response = client.post(
                "/receipts/upload",
                files={"file": (f"receipt{i}.png", io.BytesIO(file_obj.read()), content_type)}
            )
            assert response.status_code == 200
            receipt_ids.append(response.json()["receipt_id"])

        # Verify all uploads succeeded and generated unique IDs
        assert len(receipt_ids) == num_uploads
        assert len(set(receipt_ids)) == num_uploads  # All IDs are unique
