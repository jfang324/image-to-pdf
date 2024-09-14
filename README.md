## About The Project

A Python package that provides a script to convert images to PDF files as well as some helpful functions if you want to include that functionality in your own project.

## Getting Started

### Prerequisites

Before you can use this package, you need to have the following installed:

-   Python 3.9 or higher
-   Pillow 10.4.0 or higher

To run the tests, you will also need:

-   pytest
-   coverage

### Installation

To install the package, run the following command in your terminal:

1. Clone the repository:

    ```sh
    git clone https://github.com/jfang324/image_to_pdf.git
    ```

2. Navigate to the project directory:

    ```sh
    cd image_to_pdf
    ```

3. Install the package:

    ```sh
    pip install .
    ```

4. The script will now be installed in your python scripts directory where you can run it or add it to your PATH to be able to run it from anywhere.

5. To run the tests, install the development dependencies:

    ```sh
    pip install -r requirements-dev.txt
    ```

6. Run the tests:

    ```sh
    coverage run --branch --source=src -m pytest
    ```

7. Generate a coverage report:

    ```sh
    coverage report -m
    ```

## Gallery & Demonstrations

https://github.com/user-attachments/assets/b497f280-93e8-46cb-9d8c-180014e79df1

## Contact

Jeffery Fang - [jefferyfang02@gmail.com](mailto:jefferyfang02@gmail.com)

## Tools & Technologies

-   Python
-   Pillow
-   pytest
-   coverage
-   Poetry
