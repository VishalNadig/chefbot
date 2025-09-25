import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fastapi.responses import FileResponse, StreamingResponse
from io import BytesIO
from pprint import pprint
from datetime import timedelta
class Chefbot():
    def __init__(self):
        self.HOME = os.path.expanduser("~")
        self.CSV_FILE = os.path.join(os.path.dirname(__file__), r"Modified_Indian_Food_Dataset.csv")
        self.MARKDOWN_FILE_PATH = os.path.join(self.HOME, r"recipes")
        self.IMAGE_DIRECTORY = r"images/"
        self.DATAFRAME = pd.read_csv(self.CSV_FILE)
        self.DATAFRAME.sort_values(by=["TotalTimeInMins"])


    def fetch_the_menu(self, dish: str = None):
        """Search for your favourite dish to make!

        Args:
            dish: Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.

        Returns:
            Dictionary of dishes.
        """
        dish_dictionary = {}
        filtered_data = self.DATAFRAME[self.DATAFRAME["TranslatedRecipeName"].str.contains(dish.title())]
        dish_dictionary = {i+1: dish for i, dish in enumerate(filtered_data["TranslatedRecipeName"])}

        if dish_dictionary:
            return dish_dictionary
        else:
            return {404: "Sorry, we don't have what you are looking for!"}


    def pie_chart(self, dish: str):
        """
        Generates a pie chart based on the given dish name.

        Parameters:
        - dish (str): The name of the dish to generate the pie chart for.

        Returns:
        - StreamingResponse: The generated pie chart image in PNG format, wrapped in a StreamingResponse object.
        """
        # self.DATAFRAME.dropna(inplace=True)
        result = self.DATAFRAME[self.DATAFRAME["TranslatedRecipeName"].str.contains(dish.title())]
        dish_dictionary = {}
        for index_number in result.index:
            dish_dictionary[result["TranslatedRecipeName"][index_number]] = result["TotalTimeInMins"][index_number]
        labels = list(dish_dictionary.keys())
        values = list(dish_dictionary.values())

        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct=lambda pct: str(int(pct * sum(values) / 100)) + " Minutes", startangle=90)
        ax1.axis('equal')

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")


    def fetch_recipe(self, dish: str = None, index_number: int = None):
        """Return the recipe for the dish entered. On the console.

        Args:
            dish : Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.
            index_number : Index number for the dish.

        Returns:
            Recipe for the dish.
        """
        if not dish:
            dish = input("Please enter the dish you would like to make: ")
        data_dictionary = self.fetch_the_menu(dish=dish)
        if not index_number:
            pprint(data_dictionary)
            index_number = int(input("Please enter the index number of the dish you would like to make: "))
        # self.DATAFRAME.dropna(inplace=True)
        filtered_dataframe = self.DATAFRAME[self.DATAFRAME["TranslatedRecipeName"].str.contains(dish.title())]
        if filtered_dataframe.empty:
            return {404: "Sorry, we don't have what you are looking for!"}

        chosen_dish = filtered_dataframe.iloc[index_number - 1]["TranslatedRecipeName"]
        minutes = filtered_dataframe.iloc[index_number - 1]["TotalTimeInMins"]
        hours = self.convert_minutes_to_hours(minutes)
        if "/" in chosen_dish:
            chosen_dish = chosen_dish.replace("/", "")
        markdown_file_path = f"{self.MARKDOWN_FILE_PATH}/{chosen_dish}.md"
        if not os.path.exists(markdown_file_path):
            os.makedirs(self.MARKDOWN_FILE_PATH, exist_ok=True)
        ingredients = filtered_dataframe.iloc[index_number - 1]["Cleaned-Ingredients"]
        instructions = filtered_dataframe.iloc[index_number - 1]["TranslatedInstructions"]
        if os.path.isfile(markdown_file_path):
            return FileResponse(markdown_file_path)
        else:
            ingredients_str = ""
            instructions_str = ""
            print(instructions.split("."))
            for instruction in instructions.split("."):
                if "\n" in instruction:
                    instruction = instruction.replace("\n", "")
                if "\r" in instruction:
                    instruction = instruction.replace("\r", "")
                if not instruction == "":
                    instructions_str += "* " + instruction + ".\n"
            for ingredient in ingredients.split(","):
                ingredients_str += "\n* " + ingredient

            with open(markdown_file_path, "w") as file:
                file.write(f"""# {chosen_dish}\n\n## Cooking time: {minutes} minutes ({hours}H {int(minutes%60)}M).\n\n## Ingredients:\n{ingredients_str}\n\n## Cooking Instructions:\n{instructions_str}""")
            return FileResponse(markdown_file_path)


    def download_recipe(self, dish: str, index_number: int):
        """Download the recipe to the device in markdown format for the dish entered.

        Args:
            dish : Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.
            index_number : Index number for the dish.

        Returns:
            Download file for the recipe.
        """
        # self.DATAFRAME.dropna(inplace=True)
        dish_matches = self.DATAFRAME[self.DATAFRAME["TranslatedRecipeName"].str.contains(dish.title())]
        dish_matches = dish_matches.reset_index(drop=True)
        if not dish_matches.empty:
            ingredients_str = ""
            chosen_dish = dish_matches.loc[index_number, "TranslatedRecipeName"]
            cooking_time = dish_matches.loc[index_number, "TotalTimeInMins"]
            hours = self.convert_minutes_to_hours(cooking_time)
            ingredients = dish_matches.loc[index_number, "Cleaned-Ingredients"]
            instructions = dish_matches.loc[index_number, "TranslatedInstructions"]
            for ingredient in ingredients.split(","):
                ingredients_str += "* " + ingredient+"\n"
            if "/" or "/ " in chosen_dish:
                chosen_dish = chosen_dish.replace("/", "")
            with open(
                rf"{self.MARKDOWN_FILE_PATH}/{chosen_dish}.md",
                "w",
            ) as file:
                file.write(
                    f"""# {chosen_dish}\n\n## Cooking time: {cooking_time} minutes ({hours}H {int(cooking_time%60)}M).\n\n## Ingredients:\n{ingredients_str}\n\n## Cooking Instructions:\n{instructions}"""
                )
            return FileResponse(
                f"{self.MARKDOWN_FILE_PATH}/{chosen_dish}.md",
                media_type="application/octet-stream",
                filename=f"{chosen_dish}.md",
            )
        else:
            return {404: "Sorry, we don't have what you are looking for!"}


    def clear_the_table(self):
        """
        Clears the menu by removing all markdown files from the specified directory.

        Returns:
            dict: A dictionary containing the status code and a message indicating the success of the operation.
                The status code 200 indicates that the menu was successfully cleared.
                The message "Table cleared!" is returned as the success message.
        """
        for file in os.listdir(self.MARKDOWN_FILE_PATH):
            os.remove(os.path.join(self.MARKDOWN_FILE_PATH, file))
        return {200: "Table cleared!"}


    def search_with_ingredients(self, ingredients: list):
        """
        Searches for dishes based on a list of ingredients.

        Parameters:
            ingredients (list): A list of ingredients to search for.

        Returns:
            dict: A dictionary containing information about the search result. If dishes are found, the dictionary will contain the dish names and a success message. If no dishes are found, the dictionary will contain an error message.
        """
        # self.DATAFRAME.dropna(inplace=True)
        contains = [self.DATAFRAME['Cleaned-Ingredients'].str.contains(ingredient) for ingredient in ingredients]
        result = self.DATAFRAME[np.all(contains, axis=0)]
        dish_names = self.fetch_menu_names(result)
        if len(dish_names) > 0:
            print(f"The dishes you can make with the given ingredients {", ".join(ingredient.title() for ingredient in ingredients)} are: \n")
            pprint(dish_names)
            try:
                dish_index = int(input("\nEnter the index number of the dish you would like to make: "))
                if dish_index in dish_names.keys():
                    cleaned_dish_name = dish_names[dish_index]#.replace('/', '').split("- ")
                    if f"{self.MARKDOWN_FILE_PATH}/{cleaned_dish_name}.md" in os.listdir(self.MARKDOWN_FILE_PATH):
                        # os.system(f"code '{self.MARKDOWN_FILE_PATH}/{cleaned_dish_name}.md'")
                        return {200: f"You have chosen to make {cleaned_dish_name}. You can find it in {self.MARKDOWN_FILE_PATH}"}
                    else:
                        self.fetch_recipe(dish=cleaned_dish_name, index_number=1)
                        return {200: f"You have chosen to make {cleaned_dish_name}. You can find it in {self.MARKDOWN_FILE_PATH}"}
                else:
                    return {404: "Sorry, we don't have what you are looking for!"}
            except Exception as e:
                return {404: f"Sorry, we don't have what you are looking for! {e}" }
        else:
            return {404: "Sorry, we don't have what you are looking for!"}


    def fetch_menu_names(self, dataframe):
        """
        Fetches and returns a list of menu names from the given dataframe.

        Parameters:
            dataframe (pd.DataFrame): The dataframe containing the menu data.

        Returns:
            list: A list of menu names in the format "{count} - {dish_name}".
        """
        dish_names = {}
        count = 1
        dish_dictionary = dataframe.set_index("TranslatedRecipeName").T.to_dict("list")
        for dish_name in dish_dictionary.keys():
            dish_name = self.fetch_the_menu(dish=dish_name)
            if 404 in dish_name.keys():
                continue
            else:
                dish_names[count] = dish_name[1]
                count+=1
        return dish_names


    def add_recipes(self, recipe_name: str, ingredients: list, cooking_time: int, cuisine: str, translated_instructions: str, cleaned_ingredients: list, dataframe: pd.DataFrame):
        """
        Adds a recipe to the given dataframe.

        Args:
            recipe_name (str): The name of the recipe.
            ingredients (list): The list of ingredients for the recipe.
            cooking_time (int): The cooking time of the recipe in minutes.
            cuisine (str): The cuisine of the recipe.
            translated_instructions (str): The translated instructions for the recipe.
            cleaned_ingredients (list): The list of cleaned ingredients for the recipe.
            dataframe (pd.DataFrame): The dataframe to which the recipe will be added.

        Returns:
            None
        """
        dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
        new_recipe = pd.DataFrame([[recipe_name, ingredients, cooking_time, cuisine, translated_instructions, cleaned_ingredients, len(cleaned_ingredients)]], columns=dataframe.columns)
        dataframe = pd.concat([dataframe, new_recipe], ignore_index=True)
        dataframe= self.update_dataframe(dataframe)
        dataframe.to_csv(fr"{self.CSV_FILE}", index=False)


    def get_recipes_with_cuisine(self, cuisine: str = None):
        """
        Retrieves recipes with a specified cuisine.

        Args:
            cuisine (str, optional): The cuisine to filter the recipes by.
                Defaults to None.

        Returns:
            dict or set: If a cuisine is specified, a dictionary containing
                recipe names as values and an incremental count as keys.
                If no cuisine is specified or cuisine is empty, a set of
                unique cuisines available in the dataset.
        """
        cuisine_set = set()
        return_dictionary = {}

        if cuisine and cuisine.strip():
            cuisine = cuisine.title()
            cuisine_data = self.DATAFRAME[self.DATAFRAME["Cuisine"] == cuisine]
            for count, recipe in enumerate(cuisine_data["TranslatedRecipeName"].str.split(","), start=1):
                return_dictionary[count] = recipe[0]
            return return_dictionary
        else:
            # self.DATAFRAME.dropna(inplace=True)
            cuisine_set = set(self.DATAFRAME['Cuisine'].unique())
            return cuisine_set


    def convert_minutes_to_hours(self, minutes):
        """
        Convert the given number of minutes to hours.

        Parameters:
            minutes (int): The number of minutes to be converted.

        Returns:
            int: The corresponding number of hours.
        """
        # Create a timedelta object with the specified number of minutes
        time_delta = timedelta(minutes=int(minutes))

        # Extract hours and minutes from the timedelta
        hours, minutes = divmod(time_delta.seconds, 3600)

        return hours


    def update_category(self, row):
        """
        Updates the category of a row based on the value in the 'TranslatedRecipeName' column.

        Parameters:
            row (pandas.Series): A row of a pandas DataFrame containing recipe information.

        Returns:
            str: The updated category of the row.
        """
        if 'Cow' in row['TranslatedRecipeName']:
            return 'Non Veg'
        else:
            return 'Veg'


    def update_dataframe(self, dataframe):
        """
        Updates the dataframe by applying the update_category function to each row.

        Parameters:
            dataframe (pandas.DataFrame): The dataframe to be updated.

        Returns:
            pandas.DataFrame: The updated dataframe.
        """
        dataframe['Category'] = dataframe.apply(self.update_category, axis=1)
        return dataframe


if __name__ == "__main__":
    cb = Chefbot()
    cb.fetch_recipe(dish="dosa", index_number=63)
    # print(cb.search_with_ingredients(ingredients=['basil']))

#  TODO: Convert pandas to polars.
