# About
My mother is a chef who has hundreds of screenshots of recipes and pdfs from cookbook scans on her computer.
In order to help her organize her recipes, I wrote this tool to automate the conversion of these files into a common format
that she can add her modifications or notes to: word documents.

The resulting image to text conversion isn't perfect but it's better than her having to type all of the information by hand.
Because there are mistakes in the conversion, the original images are saved at the bottom of each word doc.

# Directory structure
To simplify things for the target user, the directory structure is hardcoded.
The code will operate in `~/Desktop/recipes/convert_images_to_doc`
where the images to convert are expected to be in `recipes_to_convert`.
The resulting Word documents will be added to `converted_recipes`.

# Installation
In addition to the python dependencies, this code requires tesseract and poppler which on Mac can be installed with `brew install tesseract` and `brew install poppler`.