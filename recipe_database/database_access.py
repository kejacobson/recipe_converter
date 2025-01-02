import os
from typing import List, Tuple
import sqlite3
from docx import Document


def extract_text(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)


def get_file_name_from_path(file_path) -> str:
    return os.path.basename(file_path)


def find_docx_files_in_directory(directory):
    docx_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".docx") and not file.startswith("~$"):
                docx_files.append(os.path.join(root, file))

    return docx_files


class RecipeDatabaseAccesser:
    """
    This classes serves as an interface to the recipe SQL database
    """

    def __init__(self, db="recipes.db"):
        self.db = db
        self._initialize_the_recipe_field_if_it_doesnt_exist()

    def _initialize_the_recipe_field_if_it_doesnt_exist(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY,
                name TEXT,
                content TEXT,
                file_path TEXT,
                web_address TEXT,
                tags TEXT
            )"""
        )

        conn.commit()
        conn.close()

    def add_recipe(self, recipe_name, text_content="", file_path="", web_address="", tags=""):
        if self._recipe_already_exists(recipe_name):
            self._update_recipe(recipe_name, text_content, file_path, web_address, tags)
        else:
            self._add_new_recipe(recipe_name, text_content, file_path, web_address, tags)

    def _recipe_already_exists(self, recipe_name: str) -> bool:
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT tags FROM recipes WHERE name=?", (recipe_name,))
            result = cursor.fetchone()
            conn.close()

            return result is not None

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def _add_new_recipe(self, recipe_name, text_content, file_path="", web_address="", tags=""):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO recipes (name, content, file_path, web_address, tags)
            VALUES (?, ?, ?, ?, ?)
            """,
            (recipe_name, text_content, file_path, web_address, tags),
        )
        conn.commit()
        conn.close()

    def _update_recipe(self, recipe_name, text_content, file_path="", web_address="", tags=""):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute(
            """
                UPDATE recipes
                SET content = ?, file_path = ?, web_address = ?, tags = ?
                WHERE name = ?
                """,
            (text_content, file_path, web_address, tags, recipe_name),
        )
        conn.commit()
        conn.close()

    def get_list_of_recipe_names_filtered_by_search_term(self, db_path, search_term: str) -> List[str]:
        """
        Retrieve the list of recipes given a search term.
        Query the SQL database fields: name, word doc content, and tags
        """
        try:
            # search term with wildcards
            search_term_clean = f"%{search_term.strip().lower()}%"

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name
                FROM recipes
                WHERE name LIKE ? OR content LIKE ? OR tags LIKE ?
                """,
                (
                    search_term_clean,
                    search_term_clean,
                    search_term_clean,
                ),
            )
            recipes = cursor.fetchall()
            conn.close()

            return [recipe[0] for recipe in recipes]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def get_recipe_details(self, recipe_name: str) -> Tuple[str, str, str]:
        """
        Find the word doc file path, web address and tags of a given recipe
        """
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, web_address, tags FROM recipes WHERE name=?", (recipe_name,))
            result = cursor.fetchone()
            conn.close()

            if result is None:
                return "", "", ""

            file_path, web_address, tags = result
            return file_path, web_address, tags

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "", "", ""

    def update_database(self, directory="recipes"):
        docs = find_docx_files_in_directory(directory)

        for doc in docs:
            text = extract_text(doc)
            name = get_file_name_from_path(doc).split(".")[0]
            self.add_recipe(name, text, doc)

    def update_tags(self, recipe_name, tags):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute(
            """
                UPDATE recipes
                SET tags = ?
                WHERE name = ?
                """,
            (tags, recipe_name),
        )
        conn.commit()
        conn.close()

    def delete_recipe(self, recipe_name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recipes WHERE name=?", (recipe_name,))
        conn.commit()
        conn.close()
