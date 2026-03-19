import os
from PIL import Image
import pytest
from unittest.mock import patch, MagicMock
from src.image_to_pdf.services.file_access_service import (
    is_image,
    convert_images_to_pdf,
)

# Mock data
mock_image_list: list[str] = ["image1.jpg", "image2.png", "image3.jpeg"]
mock_directory: str = "/path/to/directory"


class TestIsImage:
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("imghdr.what", return_value="JPEG")
    def test_is_image_with_valid_file_returns_true(
        self, mock_exists: MagicMock, mock_isfile: MagicMock, mock_what: MagicMock
    ):
        assert is_image(mock_image_list[0])

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=False)
    def test_is_image_with_invalid_file_returns_false(
        self, mock_exists: MagicMock, mock_isfile: MagicMock
    ):
        assert not is_image(mock_image_list[0])


class TestConvertImagesToPdf:
    @patch("os.path.isdir", return_value=True)
    @patch("src.image_to_pdf.services.file_access_service.is_image", return_value=True)
    @patch("PIL.Image.open", return_value=Image.new("RGB", (100, 100)))
    @patch("PIL.Image.Image.save", return_value=None)
    @patch("os.path.join", return_value="/path/to/output.pdf")
    def test_convert_images_to_pdf_with_valid_file_list_and_output_path_and_name(
        self,
        mock_join: MagicMock,
        mock_save: MagicMock,
        mock_open: MagicMock,
        mock_is_image: MagicMock,
        mock_isdir: MagicMock,
    ):
        convert_images_to_pdf(mock_image_list, "/path/to/output", "output")

        assert mock_is_image.call_count == 3
        assert mock_open.call_count == 6

    @patch("os.path.isdir", return_value=True)
    @patch("src.image_to_pdf.services.file_access_service.is_image", return_value=False)
    @patch("PIL.Image.open", return_value=Image.new("RGB", (100, 100)))
    @patch("PIL.Image.Image.save", return_value=None)
    @patch("os.path.join", return_value="/path/to/output.pdf")
    def test_convert_images_to_pdf_with_invalid_file_list_skips_invalid_files(
        self,
        mock_join: MagicMock,
        mock_save: MagicMock,
        mock_open: MagicMock,
        mock_is_image: MagicMock,
        mock_isdir: MagicMock,
    ):
        convert_images_to_pdf(mock_image_list, "/path/to/output", "output")

        assert mock_open.call_count == 0
        assert mock_save.call_count == 0
