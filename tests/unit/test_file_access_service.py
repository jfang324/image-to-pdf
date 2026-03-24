from pathlib import Path

import pytest
from PIL import Image

from src.image_to_pdf.services.file_access_service import (
    convert_images_to_pdf,
    is_image,
)


class TestIsImage:
    def test_is_image_returns_true_for_png(self, tmp_path: Path) -> None:
        img_path = tmp_path / "test.png"
        Image.new("RGB", (10, 10)).save(img_path)
        assert is_image(str(img_path)) is True

    def test_is_image_returns_true_for_jpeg(self, tmp_path: Path) -> None:
        img_path = tmp_path / "test.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")
        assert is_image(str(img_path)) is True

    def test_is_image_returns_true_for_gif(self, tmp_path: Path) -> None:
        img_path = tmp_path / "test.gif"
        Image.new("RGB", (10, 10)).save(img_path, format="GIF")
        assert is_image(str(img_path)) is True

    def test_is_image_returns_false_for_nonexistent_file(self) -> None:
        assert is_image("/nonexistent/file.png") is False

    def test_is_image_returns_false_for_text_file(self, tmp_path: Path) -> None:
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("not an image")
        assert is_image(str(txt_path)) is False

    def test_is_image_returns_false_for_directory(self, tmp_path: Path) -> None:
        assert is_image(str(tmp_path)) is False


class TestConvertImagesToPdf:
    def test_convert_images_to_pdf_raises_on_empty_list(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="image_paths cannot be empty"):
            convert_images_to_pdf([], str(tmp_path), "output")

    def test_convert_images_to_pdf_raises_on_invalid_quality_low(self, tmp_path: Path) -> None:
        img_path = tmp_path / "image.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")

        with pytest.raises(ValueError, match="quality must be between 1 and 100"):
            convert_images_to_pdf([str(img_path)], str(tmp_path), "output", quality=0)

    def test_convert_images_to_pdf_raises_on_invalid_quality_high(self, tmp_path: Path) -> None:
        img_path = tmp_path / "image.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")

        with pytest.raises(ValueError, match="quality must be between 1 and 100"):
            convert_images_to_pdf([str(img_path)], str(tmp_path), "output", quality=101)

    def test_convert_images_to_pdf_raises_on_invalid_output_path(self) -> None:
        with pytest.raises(ValueError, match="output_path must be a valid directory"):
            convert_images_to_pdf(["image.jpg"], "/nonexistent/path", "output")

    def test_convert_images_to_pdf_raises_on_empty_output_name(self, tmp_path: Path) -> None:
        img_path = tmp_path / "image.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")

        with pytest.raises(ValueError, match="output_name cannot be empty"):
            convert_images_to_pdf([str(img_path)], str(tmp_path), "")

    def test_convert_images_to_pdf_raises_on_whitespace_only_output_name(
        self, tmp_path: Path
    ) -> None:
        img_path = tmp_path / "image.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")

        with pytest.raises(ValueError, match="output_name cannot be empty"):
            convert_images_to_pdf([str(img_path)], str(tmp_path), "   ")

    def test_convert_images_to_pdf_raises_on_name_collision(self, tmp_path: Path) -> None:
        existing_file = "report"
        full_path = tmp_path / f"{existing_file}.pdf"
        full_path.touch()

        img_path = tmp_path / "image.jpg"
        Image.new("RGB", (10, 10)).save(img_path, format="JPEG")

        with pytest.raises(ValueError, match="already exists"):
            convert_images_to_pdf([str(img_path)], str(tmp_path), existing_file)

    def test_convert_images_to_pdf_raises_when_all_files_invalid(self, tmp_path: Path) -> None:
        txt_path = tmp_path / "not_an_image.txt"
        txt_path.write_text("not an image")

        output_path = tmp_path / "output"
        output_path.mkdir()

        with pytest.raises(ValueError, match="None of the selected files"):
            convert_images_to_pdf([str(txt_path)], str(output_path), "output")

    def test_convert_images_to_pdf_skips_nonexistent_images(self, tmp_path: Path) -> None:
        valid_path = tmp_path / "valid.jpg"
        Image.new("RGB", (10, 10)).save(valid_path, format="JPEG")

        output_path = tmp_path / "output"
        output_path.mkdir()

        pdf_path = output_path / "output.pdf"
        convert_images_to_pdf(
            ["/nonexistent/image.jpg", str(valid_path)], str(output_path), "output"
        )
        assert pdf_path.exists()

    def test_convert_images_to_pdf_creates_valid_pdf(self, tmp_path: Path) -> None:
        img1_path = tmp_path / "image1.jpg"
        img2_path = tmp_path / "image2.png"
        Image.new("RGB", (100, 100), color="red").save(img1_path, format="JPEG")
        Image.new("RGB", (100, 100), color="blue").save(img2_path)

        output_path = tmp_path / "output"
        output_path.mkdir()

        convert_images_to_pdf(
            [str(img1_path), str(img2_path)],
            str(output_path),
            "combined",
        )
        pdf_path = output_path / "combined.pdf"
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0

    def test_convert_images_to_pdf_preserves_image_order(self, tmp_path: Path) -> None:
        colors = ["red", "green", "blue"]
        img_paths = []
        for i, color in enumerate(colors):
            img_path = tmp_path / f"image{i}.jpg"
            Image.new("RGB", (50, 50), color=color).save(img_path, format="JPEG")
            img_paths.append(str(img_path))

        output_path = tmp_path / "output"
        output_path.mkdir()

        convert_images_to_pdf(
            [img_paths[2], img_paths[0], img_paths[1]],
            str(output_path),
            "ordered",
        )
        pdf_path = output_path / "ordered.pdf"
        assert pdf_path.exists()

    def test_convert_images_to_pdf_converts_rgba_mode(self, tmp_path: Path) -> None:
        img_path = tmp_path / "image.png"
        Image.new("RGBA", (50, 50), color=(255, 0, 0, 128)).save(img_path)

        output_path = tmp_path / "output"
        output_path.mkdir()

        convert_images_to_pdf([str(img_path)], str(output_path), "rgba_test")
        pdf_path = output_path / "rgba_test.pdf"
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0

    def test_convert_images_to_pdf_converts_palette_mode(self, tmp_path: Path) -> None:
        img_path = tmp_path / "image.gif"
        Image.new("P", (50, 50)).save(img_path)

        output_path = tmp_path / "output"
        output_path.mkdir()

        convert_images_to_pdf([str(img_path)], str(output_path), "palette_test")
        pdf_path = output_path / "palette_test.pdf"
        assert pdf_path.exists()
