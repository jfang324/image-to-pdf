from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from src.image_to_pdf.app import ImageToPDFApp
from src.image_to_pdf.services.file_access_service import scan_directory


class TestScanDirectory:
    def test_returns_named_tuple_of_name_path_selected(self, tmp_path: Path) -> None:
        img_path = tmp_path / "photo.jpg"
        img_path.touch()

        with patch(
            "src.image_to_pdf.services.file_access_service.is_image",
            return_value=True,
        ):
            result = scan_directory(str(tmp_path), [])
            assert result == [("photo.jpg", str(img_path), False)]

    def test_filters_hidden_files(self, tmp_path: Path) -> None:
        hidden = tmp_path / ".hidden.png"
        hidden.touch()
        visible = tmp_path / "visible.jpg"
        visible.touch()

        with patch(
            "src.image_to_pdf.services.file_access_service.is_image",
            return_value=True,
        ):
            result = scan_directory(str(tmp_path), [])
            names = [name for name, _, _ in result]
            assert ".hidden.png" not in names
            assert "visible.jpg" in names

    def test_filters_non_images(self, tmp_path: Path) -> None:
        jpg = tmp_path / "photo.jpg"
        jpg.touch()
        txt = tmp_path / "readme.txt"
        txt.touch()

        def fake_is_image(path: str) -> bool:
            return path.endswith(".jpg")

        with patch(
            "src.image_to_pdf.services.file_access_service.is_image",
            side_effect=fake_is_image,
        ):
            result = scan_directory(str(tmp_path), [])
            names = [name for name, _, _ in result]
            assert "photo.jpg" in names
            assert "readme.txt" not in names

    def test_marks_selected_files(self, tmp_path: Path) -> None:
        img_path = tmp_path / "photo.jpg"
        img_path.touch()

        with patch(
            "src.image_to_pdf.services.file_access_service.is_image",
            return_value=True,
        ):
            result = scan_directory(str(tmp_path), [str(img_path)])
            assert result == [("photo.jpg", str(img_path), True)]

    def test_raises_on_oserror(self, tmp_path: Path) -> None:
        with patch(
            "src.image_to_pdf.services.file_access_service.os.listdir",
            side_effect=OSError("Permission denied"),
        ):
            with pytest.raises(OSError, match="Permission denied"):
                scan_directory(str(tmp_path), [])


class TestOnImageSelectorSelectionChanged:
    def test_removes_deselected_files(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg", "/path/b.jpg", "/path/c.jpg"]

        mock_event = MagicMock()
        mock_event.selected_files = []
        mock_event.deselected_files = ["/path/b.jpg"]

        app._updated_current_selected_files(mock_event)
        assert app.current_selected_files == ["/path/a.jpg", "/path/c.jpg"]

    def test_appends_newly_selected_files(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg"]

        mock_event = MagicMock()
        mock_event.selected_files = ["/path/b.jpg", "/path/c.jpg"]
        mock_event.deselected_files = []

        app._updated_current_selected_files(mock_event)
        assert app.current_selected_files == [
            "/path/a.jpg",
            "/path/b.jpg",
            "/path/c.jpg",
        ]

    def test_reselecting_deselected_file_readds_it(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg", "/path/b.jpg"]

        mock_event = MagicMock()
        mock_event.selected_files = ["/path/a.jpg", "/path/b.jpg"]
        mock_event.deselected_files = ["/path/a.jpg"]

        app._updated_current_selected_files(mock_event)
        assert app.current_selected_files == ["/path/b.jpg", "/path/a.jpg"]

    def test_no_duplicates_when_reselecting(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg"]

        mock_event = MagicMock()
        mock_event.selected_files = ["/path/a.jpg"]
        mock_event.deselected_files = []

        app._updated_current_selected_files(mock_event)
        assert app.current_selected_files == ["/path/a.jpg"]


class TestOnFileOrganizerSwap:
    def test_swaps_two_files(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg", "/path/b.jpg", "/path/c.jpg"]

        mock_event = MagicMock()
        mock_event.index_1 = 0
        mock_event.index_2 = 2

        app._handle_file_reorder(mock_event)
        assert app.current_selected_files == [
            "/path/c.jpg",
            "/path/b.jpg",
            "/path/a.jpg",
        ]

    def test_swap_same_index_noops(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg", "/path/b.jpg"]

        mock_event = MagicMock()
        mock_event.index_1 = 1
        mock_event.index_2 = 1

        app._handle_file_reorder(mock_event)
        assert app.current_selected_files == ["/path/a.jpg", "/path/b.jpg"]


class TestOnSaveModalClose:
    def test_returns_early_on_none(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg"]

        with (
            patch.object(app, "notify") as mock_notify,
            patch.object(app, "_handle_save_request") as mock_save,
        ):
            app._on_save_modal_close(None)
            mock_notify.assert_not_called()
            mock_save.assert_not_called()

    def test_notify_error_on_empty_selection(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = []

        with (
            patch.object(app, "notify") as mock_notify,
            patch.object(app, "_handle_save_request") as mock_save,
        ):
            app._on_save_modal_close("output")
            mock_notify.assert_called_once()
            assert "No files selected" in mock_notify.call_args[0][0]
            mock_save.assert_not_called()

    def test_calls_handle_save_request_and_notify_on_valid(self) -> None:
        app = ImageToPDFApp()
        app.current_selected_files = ["/path/a.jpg"]
        app.output_directory = "/tmp"

        with (
            patch.object(app, "notify") as mock_notify,
            patch.object(app, "_handle_save_request") as mock_save,
        ):
            app._on_save_modal_close("my_report")
            mock_save.assert_called_once_with(
                ["/path/a.jpg"],
                "/tmp",
                "my_report",
                app.config.quality,
                app.config.optimize,
            )
            mock_notify.assert_called_once()
            assert "Job started" in mock_notify.call_args[0][0]


class TestIntegration:
    @pytest.mark.asyncio
    async def test_save_flow_creates_pdf(self, tmp_path: Path) -> None:
        img_path = tmp_path / "photo.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        app = ImageToPDFApp()

        with patch("src.image_to_pdf.app.convert_images_to_pdf") as mock_convert:
            async with app.run_test():
                app.output_directory = str(output_dir)
                app.current_selected_files = [str(img_path)]

                worker = app._handle_save_request(
                    [str(img_path)],
                    str(output_dir),
                    "report",
                    app.config.quality,
                    app.config.optimize,
                )
                await worker.wait()

                mock_convert.assert_called_once_with(
                    [str(img_path)],
                    str(output_dir),
                    "report",
                    app.config.quality,
                    app.config.optimize,
                )
