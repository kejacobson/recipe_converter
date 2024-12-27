from recipe_database.database_access import extract_text, store_recipe_in_db
import os

def find_docx_files_in_directory(directory):
    docx_files = []
    
    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.docx') and not file.startswith('~$'):
                # Get the full path of the docx file
                docx_files.append(os.path.join(root, file))
    
    return docx_files


def get_file_name_from_path(file_path) -> str:
    return os.path.basename(file_path)

def main():
    database = "recipes.db"
    docs = find_docx_files_in_directory("recipes")

    for doc in docs:
        text = extract_text(doc)
        name = get_file_name_from_path(doc).split(".")[0]
        store_recipe_in_db(database, name, text, doc)



if __name__ == "__main__":
    main()