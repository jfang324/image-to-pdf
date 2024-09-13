from setuptools import setup, find_packages

setup(
    name="image_to_pdf",
    version="1.0",
    author="jfang324",
    author_email="jefferyfang324@gmail.com",
    description="A Python package for converting images to PDF files.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["Pillow"],
    url="https://github.com/jfang324/image_to_pdf",
    entry_points={
        "console_scripts": [
            "image_to_pdf = image_to_pdf.main:main",
        ]
    },
    python_requires=">=3.9",
)
