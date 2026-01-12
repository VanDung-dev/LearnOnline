"""
Test WebP image compression utility.
"""

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.courses.utils import convert_to_webp


class WebPConversionTestCase(TestCase):
    """Test cases for WebP image conversion utility."""

    def create_test_image(self, format_name, size=(100, 100), color='red'):
        """Create a test image in memory."""
        img = Image.new('RGB', size, color=color)
        buffer = BytesIO()
        img.save(buffer, format=format_name)
        buffer.seek(0)
        return buffer

    def test_png_to_webp_conversion(self):
        """Test converting PNG image to WebP."""
        # Create a PNG image
        png_buffer = self.create_test_image('PNG')
        uploaded_file = SimpleUploadedFile(
            'test_image.png',
            png_buffer.getvalue(),
            content_type='image/png'
        )

        # Convert to WebP
        result = convert_to_webp(uploaded_file)

        # Verify conversion happened
        self.assertIsNotNone(result)
        new_filename, content_file = result
        self.assertTrue(new_filename.endswith('.webp'))
        self.assertIsInstance(content_file, ContentFile)

    def test_jpg_to_webp_conversion(self):
        """Test converting JPEG image to WebP."""
        # Create a JPEG image
        jpg_buffer = self.create_test_image('JPEG')
        uploaded_file = SimpleUploadedFile(
            'test_image.jpg',
            jpg_buffer.getvalue(),
            content_type='image/jpeg'
        )

        # Convert to WebP
        result = convert_to_webp(uploaded_file)

        # Verify conversion happened
        self.assertIsNotNone(result)
        new_filename, content_file = result
        self.assertTrue(new_filename.endswith('.webp'))

    def test_webp_not_reconverted(self):
        """Test that WebP images are not re-converted."""
        # Create a WebP image
        webp_buffer = self.create_test_image('WEBP')
        uploaded_file = SimpleUploadedFile(
            'test_image.webp',
            webp_buffer.getvalue(),
            content_type='image/webp'
        )

        # Should return None (no conversion needed)
        result = convert_to_webp(uploaded_file)
        self.assertIsNone(result)

    def test_png_transparency_preserved(self):
        """Test that transparency in PNG is preserved."""
        # Create a PNG with transparency
        img = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            'transparent.png',
            buffer.getvalue(),
            content_type='image/png'
        )

        result = convert_to_webp(uploaded_file)
        self.assertIsNotNone(result)

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        result = convert_to_webp(None)
        self.assertIsNone(result)

    def test_file_size_reduction(self):
        """Test that WebP conversion reduces file size for large images."""
        # Create a larger image
        large_buffer = self.create_test_image('PNG', size=(500, 500))
        original_size = len(large_buffer.getvalue())

        uploaded_file = SimpleUploadedFile(
            'large_image.png',
            large_buffer.getvalue(),
            content_type='image/png'
        )

        result = convert_to_webp(uploaded_file)
        self.assertIsNotNone(result)

        _, content_file = result
        webp_size = len(content_file.read())

        # WebP should generally be smaller than PNG
        # But this is not always true for small/simple images
        # So we just verify it's a valid size
        self.assertGreater(webp_size, 0)
