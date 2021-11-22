#!/usr/bin/env python
import cv2
import pytesseract
import docx
import re
import os
from pdf2image import convert_from_path
from contextlib import contextmanager

@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)

class RecipeConverter:
    def __init__(self):
        self.folder = 'recipes_to_convert'
        self.word_folder = 'converted_recipes'

    def run(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        with cd(dir_path):
            self.remove_ds_store()
            files = os.listdir(self.folder)

            for filename in files:
                image_file = f'{self.folder}/{filename}'
                word_file = f'{self.word_folder}/{filename}'
                text = self.read_text_from_image(image_file)
                self.write_text_to_word_doc(text, word_file, image_file)

    def remove_ds_store(self):
        ds_store = f'{self.folder}/.DS_Store'
        if os.path.exists(ds_store):
            os.system(f'rm {ds_store}')

    def get_file_root(self, file):
        return os.path.splitext(file)[0]

    def get_word_file_name(self, image_file):
        return self.get_file_root(image_file) + '.docx'

    def convert_pdf_name_to_image(self, image_filename):
        return self.get_file_root(image_filename)+'.jpg'

    def make_string_xml_compatible(self, line):
        re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', line)

    def convert_pdf_to_image(self, image_filename):
        if image_filename[-3:] == 'pdf':
            images = convert_from_path(image_filename)
            jpg_file = self.get_file_root(image_filename) +'.jpg'
            images[0].save(jpg_file, 'JPEG')
            return jpg_file
        else:
            return image_filename
        
    def read_text_from_image(self, image_filename):
        image_filename = self.convert_pdf_to_image(image_filename)
        print('Reading', image_filename)
        img = cv2.imread(image_filename)
        text:str = pytesseract.image_to_string(img)
        return text

    def write_text_to_word_doc(self, text, image_filename, full_image_path):
        if image_filename[-3:] == 'pdf':
            full_image_path = self.convert_pdf_name_to_image(full_image_path)
        doc = docx.Document()
        re.sub('\n\n','\n',text)
        for line in text.splitlines():
            self.make_string_xml_compatible(line)
            doc.add_paragraph(line)
        doc.add_picture(full_image_path, width=docx.shared.Inches(7))
        word_file = self.get_word_file_name(image_filename)
        doc.save(word_file)


if __name__ == '__main__':
    converter = RecipeConverter()
    converter.run()
