import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import sqlite3

from recipe_database.database_access import RecipeDatabaseAccesser, extract_text
from recipe_database.convert_recipes import RecipeConverter


class RecipeDatabaseGui:
    def __init__(self):
        self.db_access = RecipeDatabaseAccesser()

        self.search_bar_id = "search_bar"
        self.recipe_dropdown_id = "recipe_dropdown"

        sections = []
        sections.append(html.H1("The Jacobson Recipe Database"))
        sections.append(self._create_recipe_explorer_div())
        sections.append(self._create_update_recipe_database_div())
        self.full_layout = html.Div(children=sections)

    def _create_recipe_explorer_div(self):
        sections = [html.H2("Recipe Explorer")]
        sections.append(self._create_search_bar())
        sections.append(self._create_found_counter_div())
        sections.append(self._create_recipe_dropdown())
        sections.append(self._create_recipe_information_div(""))
        return html.Div(sections)

    def _create_found_counter_div(self):
        return html.Div("", id="found-counter", style={"margin-top": "20px", "margin-bottom": "20px"})

    def _create_search_bar(self):
        return dcc.Input(
            id=self.search_bar_id,
            type="text",
            placeholder="Search for a recipe...",
            debounce=True,
            style={"width": "400px", "height": "40px", "font-size": "20px"},
        )

    def _create_recipe_dropdown(self):
        return dcc.Dropdown(
            id=self.recipe_dropdown_id,
            options=[],
            value="Select a recipe",
            style={"width": "400px", "font-size": "16px"},
        )

    def _create_recipe_information_div(self, recipe_name):
        children = []
        file_path, web_address, tags = self.db_access.get_recipe_details(recipe_name)

        display = "block" if web_address else "none"
        website = html.A("View Recipe Online", href=web_address, target="_blank", style={"display": display})
        children.append(website)

        display = "block" if file_path else "none"
        children.append(html.Br())
        children.append(self._create_word_doc_open_button(display))
        children.append(self._create_word_doc_open_status())
        children.append(html.Br())
        children.append(self._create_word_doc_location_open_button(display))
        children.append(self._create_word_doc_location_open_status())
        children.append(html.Br())

        if file_path:
            full_path = os.path.abspath(file_path)
            children.append(html.Div(f"File location: {full_path}"))

        children.append(html.Br())
        children.append(html.Div(f"Tags: {tags}"))
        return html.Div(children, id="recipe-content")

    def _create_word_doc_open_button(self, display):
        return html.Button("Open Word Document", id="open-doc-button", style={"display": display})

    def _create_word_doc_open_status(self):
        return html.Div(
            "",
            id="open-doc-status",
        )

    def _create_word_doc_location_open_button(self, display):
        return html.Button("Open Word Document Location in Finder", id="open-loc-button", style={"display": display})

    def _create_word_doc_location_open_status(self):
        return html.Div(
            "",
            id="open-loc-status",
        )

    def _create_update_recipe_database_div(self):
        sections = [html.H2("Database update")]
        sections.append(html.H3("Update the database's word documents"))
        sections.append(
            html.Div(
                "This button will search the recipe directory for any updates to word documents in the recipe database. These updates can either be new word documents, or modifications to existing ones"
            )
        )
        sections.append(html.Button("Update database's word documents", id="update-word-docs-button"))
        sections.append(html.Div("", id="update-word-docs-status"))
        sections.append(self._add_website_section())
        return html.Div(sections)

    def _add_website_section(self):
        sections = []
        sections.append(html.H3("Add a website"))
        sections.append(
            dcc.Input(
                id="input-recipe-name",
                type="text",
                placeholder="Recipe name",
                debounce=True,
                style={"width": "400px", "height": "40px", "font-size": "20px"},
            )
        )
        sections.append(html.Br())
        sections.append(html.Br())
        sections.append(
            dcc.Input(
                id="input-recipe-web-address",
                type="text",
                placeholder="Recipe web address",
                debounce=True,
                style={"width": "400px", "height": "40px", "font-size": "20px"},
            )
        )
        sections.append(html.Br())
        sections.append(html.Br())
        sections.append(
            dcc.Input(
                id="input-recipe-tags",
                type="text",
                placeholder="Recipe tags",
                debounce=True,
                style={"width": "400px", "height": "40px", "font-size": "20px"},
            )
        )
        sections.append(html.Br())
        sections.append(html.Br())
        sections.append(html.Button("Add website", id="add-website-button"))
        sections.append(html.Br())
        sections.append(html.Div("", id="website-added-status"))
        return html.Div(sections)


def add_call_backs(app: dash.Dash, gui: RecipeDatabaseGui):

    @app.callback(
        Output(gui.recipe_dropdown_id, "options"),
        Output(gui.recipe_dropdown_id, "value"),
        Output("found-counter", "children"),
        Input(gui.search_bar_id, "value"),
    )
    def update_recipe_dropdown(search_term):
        """
        Update the available recipes in the dropdown given the current value of the search field
        """
        if not search_term:  # If search term is empty, return all recipes
            recipes = gui.db_access.get_list_of_recipe_names_filtered_by_search_term("recipes.db", "")
        else:
            recipes = gui.db_access.get_list_of_recipe_names_filtered_by_search_term("recipes.db", search_term)

        # Debugging: print current search term and number of results
        print(f"Search term: {search_term}, Found {len(recipes)} recipes.")

        return (
            [{"label": recipe, "value": recipe} for recipe in recipes],
            "Select a recipe",
            f"Found {len(recipes)} recipes.",
        )

    @app.callback(
        Output("recipe-content", "children"),
        Input(gui.recipe_dropdown_id, "value"),
    )
    def display_recipe_content(recipe_name):
        """
        Display the recipe content
        """
        if recipe_name == "Select a recipe" or recipe_name is None:
            return None, ""

        return gui._create_recipe_information_div(recipe_name)

    # Callback to open the Word document when the hidden button is clicked
    @app.callback(
        Output("open-doc-status", "children"),
        Input("open-doc-button", "n_clicks"),
        State(gui.recipe_dropdown_id, "value"),
    )
    def open_word_document(n_clicks, recipe_name):
        """
        Open a word document using the default application
        """
        if n_clicks:
            # Get the full path to the file
            file_path, _, _ = gui.db_access.get_recipe_details(recipe_name)
            full_file_path = os.path.abspath(file_path).replace(" ", "\ ")

            os.system(f"open {full_file_path}")  # Open the Word document
            return "Opened"

        return ""

    @app.callback(
        Output("open-loc-status", "children"),
        Input("open-loc-button", "n_clicks"),
        State(gui.recipe_dropdown_id, "value"),
    )
    def open_word_document_file_location(n_clicks, recipe_name):
        if n_clicks:
            # Get the full path to the file and open it
            file_path, _, _ = gui.db_access.get_recipe_details(recipe_name)
            full_location_path = os.path.dirname(os.path.abspath(file_path).replace(" ", "\ "))

            os.system(f"open {full_location_path}")  # Open the Word document location
            return "Opened"

        return ""

    @app.callback(
        Output("update-word-docs-status", "children"),
        Input("update-word-docs-button", "n_clicks"),
    )
    def update_word_docs_in_database(n_clicks):
        if n_clicks:
            # Get the full path to the file and open it
            gui.db_access.update_database()
            recipes = gui.db_access.get_list_of_recipe_names_filtered_by_search_term("recipes.db", "")
            return f"Updated database. {len(recipes)} found."

        return ""

    @app.callback(
        Output("website-added-status", "children"),
        Input("add-website-button", "n_clicks"),
        State("input-recipe-name", "value"),
        State("input-recipe-web-address", "value"),
        State("input-recipe-tags", "value"),
    )
    def add_website_to_database(n_clicks, recipe_name, web_address, tags):
        if n_clicks:
            converter = RecipeConverter()
            filename = converter.convert_a_website(recipe_name, web_address)
            text = extract_text(filename)

            gui.db_access.add_recipe(recipe_name, text, filename, web_address, tags)
            return f"Added {recipe_name} to database"

        return ""


if __name__ == "__main__":

    gui = RecipeDatabaseGui()
    app = dash.Dash(__name__)
    app.layout = gui.full_layout
    add_call_backs(app, gui)
    app.run_server(debug=True)
