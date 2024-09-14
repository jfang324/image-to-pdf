import os
from PIL import Image
import pytest
from unittest.mock import patch, MagicMock
from src.image_to_pdf import get_file_list, validate_path, convert_images_to_pdf

# Mock data
mock_image_list: list[str] = ["image1.jpg", "image2.png", "image3.jpeg"]
mock_directory: str = "/path/to/directory"


class TestGetFileList:
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", side_effect=[False, True, True, True])
    @patch("os.listdir", return_value=mock_image_list)
    def test_get_file_list_with_valid_directory_returns_correct_file_list(
        self, mock_listdir: MagicMock, mock_isfile: MagicMock, mock_exists: MagicMock
    ):
        assert get_file_list(mock_directory) == [
            os.path.join(mock_directory, file) for file in mock_image_list
        ]

    @patch("os.path.exists", return_value=False)
    def test_get_file_list_with_non_existing_directory_returns_empty_list(
        self, mock_exists: MagicMock
    ):
        assert get_file_list("/non/existing/directory") == []

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_get_file_list_with_file_returns_empty_list(
        self, mock_isfile: MagicMock, mock_exists: MagicMock
    ):
        assert get_file_list("/path/to/file.txt") == []


class TestValidatePath:
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_validate_path_with_valid_directory_returns_true(
        self, mock_isdir: MagicMock, mock_exists: MagicMock
    ):
        assert validate_path(mock_directory)

    @patch("os.path.exists", return_value=False)
    def test_validate_path_with_non_existing_directory_returns_false(
        self, mock_exists: MagicMock
    ):
        assert not validate_path("/invalid/directory")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=False)
    def test_validate_path_with_file_returns_false(
        self, mock_isdir: MagicMock, mock_exists: MagicMock
    ):
        assert not validate_path("/path/to/file.txt")


class TestConvertImagesToPdf:
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("PIL.Image.open", return_value=Image.new("RGB", (100, 100)))
    @patch("PIL.Image.Image.save", return_value=None)
    @patch("os.path.join", return_value="/path/to/output.pdf")
    def test_convert_images_to_pdf_with_valid_file_list_and_output_path_and_name(
        self,
        mock_join: MagicMock,
        mock_save: MagicMock,
        mock_open: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
    ):
        convert_images_to_pdf(mock_image_list, "/path/to/output", "output")

        for file in mock_image_list:
            mock_open.assert_any_call(file)

        mock_save.assert_called_once_with(
            "/path/to/output.pdf",
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=[
                Image.new("RGB", (100, 100)) for i in range(len(mock_image_list))
            ][1:],
        )

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("PIL.Image.open", return_value=Exception("Mock exception"))
    def test_convert_images_to_pdf_with_invalid_file_list_raises_exception(
        self,
        mock_open: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
    ):
        with pytest.raises(Exception):
            convert_images_to_pdf(mock_image_list, "/path/to/output", "output")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("PIL.Image.open")
    @patch("PIL.Image.Image.save", return_value=None)
    @patch("os.path.join", return_value="/path/to/output.pdf")
    def test_convert_images_to_pdf_with_save_raises_exception(
        self,
        mock_join: MagicMock,
        mock_save: MagicMock,
        mock_open: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
    ):
        mock_image: MagicMock = MagicMock()
        mock_image.save.side_effect = Exception("Mock exception")
        mock_open.return_value = mock_image

        with pytest.raises(Exception):
            convert_images_to_pdf(mock_image_list, "/path/to/output", "output")
