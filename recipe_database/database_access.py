from typing import List, Tuple
import sqlite3
from docx import Document


def extract_text(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)


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

    def add_new_recipe(self, recipe_name, text_content, file_path="", web_address="", tags=""):
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
