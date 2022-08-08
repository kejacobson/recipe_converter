from setuptools import setup, find_packages

__package_name__ = "recipe_converter"
__package_version__ = "1.0.0"


setup(
    name=__package_name__,
    version=__package_version__,
    description=("Convert images and pdfs of cooking recipes into word docs"),
    scripts=['recipe_converter/convert_recipes.py'],
    author="Kevin Jacobson",
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "python-docx",
        "pdf2image",
        "pytesseract",
        "opencv-python"
    ],
    python_requires='>=3.6'
)
