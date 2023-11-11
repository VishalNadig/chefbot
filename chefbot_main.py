import os
import pandas as pd
from fastapi import File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
from pprint import pprint
from datetime import datetime, timedelta
import cv2 as cv

CSV_FILE = r"Modified_Indian_Food_Dataset.csv"
MARKDOWN_FILE_PATH = r"recipes"
IMAGE_DIRECTORY = r"images/"


def fetch_the_menu(dish: str = None):
    """Search for your favourite dish to make!

    Args:
        dish: Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.

    Returns:
        Dictionary of dishes.
    """
    count = 1
    dish_dictionary = {}
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(inplace=True)
    for dishes in dataframe["TranslatedRecipeName"]:
        if dish.title() in dishes:
            dish_dictionary[count] = dishes
            count += 1

    if len(dish_dictionary) > 0:
        return dish_dictionary
    else:
        return {404: "Sorry, we don't have what you are looking for!"}



def pie_chart(dish: str):
    """
    Generates a pie chart based on the given dish name.

    Parameters:
    - dish (str): The name of the dish to generate the pie chart for.

    Returns:
    - StreamingResponse: The generated pie chart image in PNG format, wrapped in a StreamingResponse object.
    """
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(inplace=True)
    result = dataframe[dataframe["TranslatedRecipeName"].str.contains(dish.title())]
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


def fetch_recipe(dish: str, index_number: int):
    """Return the recipe for the dish entered. On the console.

    Args:
        dish : Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.
        index_number : Index number for the dish.

    Returns:
        Recipe for the dish.
    """
    dish_dictionary = {}
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(inplace=True)
    filtered_dataframe = dataframe[dataframe["TranslatedRecipeName"].str.contains(dish.title())]
    dish_dictionary = {count: [dishes] for count, dishes in enumerate(filtered_dataframe["TranslatedRecipeName"], 1)}

    if len(dish_dictionary) > 0 and index_number in dish_dictionary.keys():
        chosen_dish = dish_dictionary[int(index_number)][0]
        df_new = dataframe[dataframe["TranslatedRecipeName"] == chosen_dish]
        index = df_new.index[0]
        dictionary = df_new.to_dict()
        markdown_file_path = f"{MARKDOWN_FILE_PATH}/{chosen_dish}.md"
        if os.path.isfile(markdown_file_path):
            return FileResponse(markdown_file_path)
        else:

            minutes = dictionary['TotalTimeInMins'][index]
            hours = convert_minutes_to_hours(minutes)
            with open(markdown_file_path, "w") as file:
                file.write(f"""# {chosen_dish}\n\n## Cooking time: {dictionary['TotalTimeInMins'][index]} minutes ({hours}H {int(minutes%60)}M).\n\n## Ingredients:\n{dictionary['Cleaned-Ingredients'][index]}\n\n## Cooking Instructions:\n{dictionary['TranslatedInstructions'][index]}""")
            return FileResponse(markdown_file_path)
    else:
        return {404: "Sorry, we don't have what you are looking for!"}


def download_recipe(dish: str, index_number: int):
    """Download the recipe to the device in markdown format for the dish entered.

    Args:
        dish : Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.
        index_number : Index number for the dish.

    Returns:
        Download file for the recipe.
    """
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(inplace=True)
    dish_matches = dataframe[dataframe["TranslatedRecipeName"].str.contains(dish.title())]
    dish_matches = dish_matches.reset_index(drop=True)
    if not dish_matches.empty:
        chosen_dish = dish_matches.loc[index_number, "TranslatedRecipeName"]
        cooking_time = dish_matches.loc[index_number, "TotalTimeInMins"]
        hours = convert_minutes_to_hours(cooking_time)
        ingredients = dish_matches.loc[index_number, "Cleaned-Ingredients"]
        instructions = dish_matches.loc[index_number, "TranslatedInstructions"]
        if "/" in chosen_dish:
            chosen_dish = chosen_dish.replace("/", "")
        with open(
            rf"{MARKDOWN_FILE_PATH}/{chosen_dish}.md",
            "w",
        ) as file:
            file.write(
                f"""# {chosen_dish}\n\n## Cooking time: {cooking_time} minutes ({hours}H {int(cooking_time%60)}M).\n\n## Ingredients:\n{ingredients}\n\n## Cooking Instructions:\n{instructions}"""
            )
        return FileResponse(
            f"{MARKDOWN_FILE_PATH}/{chosen_dish}.md",
            media_type="application/octet-stream",
            filename=f"{chosen_dish}.md",
        )
    else:
        return {404: "Sorry, we don't have what you are looking for!"}


def clear_the_table():
    """
    Clears the menu by removing all markdown files from the specified directory.

    Returns:
        dict: A dictionary containing the status code and a message indicating the success of the operation.
            The status code 200 indicates that the menu was successfully cleared.
            The message "Table cleared!" is returned as the success message.
    """
    for file in os.listdir(MARKDOWN_FILE_PATH):
        os.remove(os.path.join(MARKDOWN_FILE_PATH, file))
    return {200: "Table cleared!"}


def search_with_ingredients(ingredients: list):
    """
    Searches for dishes based on a list of ingredients.

    Parameters:
        ingredients (list): A list of ingredients to search for.

    Returns:
        dict: A dictionary containing information about the search result. If dishes are found, the dictionary will contain the dish names and a success message. If no dishes are found, the dictionary will contain an error message.
    """
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(inplace=True)
    contains = [dataframe['Cleaned-Ingredients'].str.contains(ingredient) for ingredient in ingredients]
    result = dataframe[np.all(contains, axis=0)] 
    dish_names = fetch_menu_names(result)
    if len(dish_names) > 0:
        pprint(dish_names)
        try:
            dish_name = int(input("Enter the index number of the dish you would like to make: "))
            if dish_name in range(1, len(dish_names)+1):
                cleaned_dish_name = dish_names[dish_name-1].replace('/', '').split("- ")[1]
                print(cleaned_dish_name)
                if f"{MARKDOWN_FILE_PATH}/{cleaned_dish_name}.md" in os.listdir(MARKDOWN_FILE_PATH):
                    os.system(f"code '{MARKDOWN_FILE_PATH}/{cleaned_dish_name}.md'")
                    return {200: f"You have chosen to make {cleaned_dish_name}. You can find it in {MARKDOWN_FILE_PATH}"}
                else:
                    download_recipe(dish=cleaned_dish_name, index_number=1)
                    os.system(f"code '{MARKDOWN_FILE_PATH}/{cleaned_dish_name}.md'")
                    return {200: f"You have chosen to make {cleaned_dish_name}. You can find it in {MARKDOWN_FILE_PATH}"}
            else:
                return {404: "Sorry, we don't have what you are looking for!"}
        except:
            return {404: "Sorry, we don't have what you are looking for!"}
    else:
        return {404: "Sorry, we don't have what you are looking for!"}

def fetch_menu_names(dataframe):
    """
    Fetches and returns a list of menu names from the given dataframe.

    Parameters:
        dataframe (pd.DataFrame): The dataframe containing the menu data.

    Returns:
        list: A list of menu names in the format "{count} - {dish_name}".
    """
    dish_names = []
    count = 1
    dish_dictionary = dataframe.set_index("TranslatedRecipeName").T.to_dict("list")
    for dish_name in dish_dictionary.keys():
        dish_name = fetch_the_menu(dish=dish_name)
        if 404 in dish_name.keys():
            continue
        else:
            dish_names.append(f"{count} - {dish_name[1][0]}")
            count+=1
    return dish_names


def add_recipes(recipe_name: str, ingredients: list, cooking_time: int, cuisine: str, translated_instructions: str, cleaned_ingredients: list, dataframe: pd.DataFrame):
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
    dataframe.to_csv(fr"/home/vishal/git/chefbot/{CSV_FILE}", index=False)


def get_recipes_with_cuisine(cuisine: str = None):
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
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["Ingredient-count"])
    
    if cuisine and cuisine.strip():
        cuisine = cuisine.title()
        cuisine_data = dataframe[dataframe["Cuisine"] == cuisine]
        for count, recipe in enumerate(cuisine_data["TranslatedRecipeName"].str.split(","), start=1):
            return_dictionary[count] = recipe[0]
        return return_dictionary
    else:
        dataframe.dropna(inplace=True)
        cuisine_set = set(dataframe['Cuisine'].unique())
        return cuisine_set

def convert_minutes_to_hours(minutes):
    """
    Convert the given number of minutes to hours.

    Parameters:
        minutes (int): The number of minutes to be converted.

    Returns:
        int: The corresponding number of hours.
    """
    # Create a timedelta object with the specified number of minutes
    time_delta = timedelta(minutes=minutes)

    # Extract hours and minutes from the timedelta
    hours, minutes = divmod(time_delta.seconds, 3600)

    return hours

if __name__ == "__main__":
    pprint(fetch_recipe(dish="Dosa", index_number=51))