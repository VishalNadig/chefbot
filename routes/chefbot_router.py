import os
from typing import List, Union, Optional

import pandas as pd
import numpy as np
from fastapi import APIRouter, Body
from fastapi.responses import FileResponse

CSV_FILE = r"Modified_Indian_Food_Dataset.csv"
MARKDOWN_FILE_PATH = r"recipes"
IMAGE_DIRECTORY = r"images/"

router = APIRouter()

os.makedirs(MARKDOWN_FILE_PATH, exist_ok=True)


@router.get("/chefbot/get_dishes", tags=["chefbot"])
def fetch_the_menu(dish: str):
    """
    Returns a dict: {1: dish_name_1, 2: dish_name_2, ...}
    The indices are stable and match /chefbot/fetch_recipe.
    """
    dataframe = pd.read_csv(CSV_FILE)

    # Use the SAME sort and filter logic as fetch_recipe
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(subset=["TranslatedRecipeName", "TotalTimeInMins"], inplace=True)

    mask = dataframe["TranslatedRecipeName"].str.contains(
        dish, case=False, na=False, regex=False
    )
    filtered_data = dataframe[mask].reset_index(drop=True)

    dish_dictionary = {
        i + 1: name for i, name in enumerate(filtered_data["TranslatedRecipeName"])
    }

    if dish_dictionary:
        return dish_dictionary
    else:
        return {404: "Sorry, we don't have what you are looking for!"}


@router.post("/chefbot/fetch_recipe", tags=["chefbot"])
def fetch_recipe(dish: str, index_number: int):
    """
    Return the recipe details (JSON) for the dish at the given index,
    using the SAME filtered & sorted list as /chefbot/get_dishes.
    """
    if index_number < 1:
        return {404: "Index number must be >= 1."}

    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(
        subset=[
            "TranslatedRecipeName",
            "Cleaned-Ingredients",
            "TranslatedInstructions",
            "TotalTimeInMins",
        ],
        inplace=True,
    )

    mask = dataframe["TranslatedRecipeName"].str.contains(
        dish, case=False, na=False, regex=False
    )
    filtered_dataframe = dataframe[mask].reset_index(drop=True)

    if filtered_dataframe.empty:
        return {404: "Sorry, we don't have what you are looking for!"}

    if index_number > len(filtered_dataframe):
        return {
            404: f"Only {len(filtered_dataframe)} matches found; index {index_number} is out of range."
        }

    row = filtered_dataframe.iloc[index_number - 1]

    chosen_dish = row["TranslatedRecipeName"]
    minutes = int(row["TotalTimeInMins"])

    hours = minutes // 60
    remaining_minutes = minutes % 60

    raw_ingredients = str(row["Cleaned-Ingredients"])
    ingredients_list = [
        ing.strip() for ing in raw_ingredients.split(",") if ing.strip()
    ]

    raw_instructions = str(row["TranslatedInstructions"])
    instructions_list = []
    for step in raw_instructions.split("."):
        step = step.strip()
        if step:
            instructions_list.append(step)

    return {
        "dish_name": chosen_dish,
        "cooking_time_minutes": minutes,
        "cooking_time_formatted": f"{hours}H {remaining_minutes}M",
        "ingredients": ingredients_list,
        "instructions": instructions_list,
        "index_number": index_number,
        "match_count": len(filtered_dataframe),
    }


@router.post("/chefbot/download_recipe", tags=["chefbot"])
def download_recipe(dish: str, index_number: int):
    """
    Download the recipe in markdown format for the dish entered.

    Args:
        dish : Name of the dish. Eg: salad, pizza, pasta, sandwich, upma, idli.
        index_number : 1-based index number for the dish from /chefbot/get_dishes.

    Returns:
        Download file for the recipe or {404: "..."}.
    """
    if index_number < 1:
        return {404: "Index number must be >= 1."}

    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(subset=["TranslatedRecipeName", "Cleaned-Ingredients", "TranslatedInstructions", "TotalTimeInMins"], inplace=True)

    mask = dataframe["TranslatedRecipeName"].str.contains(
        dish, case=False, na=False, regex=False
    )
    dish_matches = dataframe[mask].reset_index(drop=True)

    if dish_matches.empty:
        return {404: "Sorry, we don't have what you are looking for!"}

    if index_number > len(dish_matches):
        return {404: f"Only {len(dish_matches)} matches found; index {index_number} is out of range."}

    row = dish_matches.iloc[index_number - 1]
    chosen_dish = row["TranslatedRecipeName"]
    cooking_time = row["TotalTimeInMins"]
    hours = convert_minutes_to_hours(cooking_time)
    ingredients = row["Cleaned-Ingredients"]
    instructions = row["TranslatedInstructions"]

    ingredients_str = ""
    for ingredient in str(ingredients).split(","):
        ingredient = ingredient.strip()
        if ingredient:
            ingredients_str += f"* {ingredient}\n"

    safe_dish_name = chosen_dish.replace("/", "").strip()
    markdown_path = os.path.join(MARKDOWN_FILE_PATH, f"{safe_dish_name}.md")

    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(
            f"# {chosen_dish}\n\n"
            f"## Cooking time: {int(cooking_time)} minutes ({hours}H {int(int(cooking_time) % 60)}M).\n\n"
            f"## Ingredients:\n{ingredients_str}\n\n"
            f"## Cooking Instructions:\n{instructions}"
        )

    return FileResponse(
        markdown_path,
        media_type="application/octet-stream",
        filename=f"{safe_dish_name}.md",
    )


@router.get("/chefbot/clear_the_menu", tags=["chefbot"])
def clear_the_table():
    """
    Clears the menu by removing all markdown files from the recipes directory.
    """
    os.makedirs(MARKDOWN_FILE_PATH, exist_ok=True)
    for file in os.listdir(MARKDOWN_FILE_PATH):
        full_path = os.path.join(MARKDOWN_FILE_PATH, file)
        if os.path.isfile(full_path):
            os.remove(full_path)
    return {200: "Table cleared!"}


@router.post("/chefbot/search_with_ingredients", tags=["chefbot"])
def search_with_ingredients(
    ingredients: List[str] = Body(
        ...,
        description="List of ingredients, e.g. ['tomato', 'onion']",
        example=["tomato", "onion", "garlic"],
    )
):
    """
    Search for dishes based on a list of ingredients sent in the request body.

    Example request body (raw JSON):
        ["tomato", "onion", "garlic"]
    """
    if not ingredients:
        return {404: "Please provide at least one ingredient."}

    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])
    dataframe.dropna(subset=["Cleaned-Ingredients", "TranslatedRecipeName"], inplace=True)

    mask = np.ones(len(dataframe), dtype=bool)
    for ing in ingredients:
        mask &= dataframe["Cleaned-Ingredients"].str.contains(
            ing, case=False, na=False, regex=False
        )

    result = dataframe[mask]

    if result.empty:
        return {404: "Sorry, we don't have what you are looking for!"}

    dishes = {
        i + 1: name
        for i, name in enumerate(result["TranslatedRecipeName"].tolist())
    }
    return dishes

@router.get("/chefbot/get_cuisines", tags=["chefbot"])
def get_cuisines():
    """
    Get a list of all unique cuisines in the dataset.

    Returns:
        {
            "cuisines": ["Indian", "Italian", "Mexican", ...],
            "count": 12
        }
    """
    dataframe = pd.read_csv(CSV_FILE)

    if "Cuisine" not in dataframe.columns:
        return {404: "Cuisine column not found in dataset."}

    # Drop rows where Cuisine is NaN, then get unique values
    dataframe = dataframe.dropna(subset=["Cuisine"])
    cuisines = sorted(dataframe["Cuisine"].unique().tolist())

    return {
        "cuisines": cuisines,
        "count": len(cuisines),
    }
def add_recipes(
    recipe_name: str,
    ingredients: List[str],
    cooking_time: int,
    cuisine: str,
    translated_instructions: str,
    cleaned_ingredients: List[str],
    dataframe: pd.DataFrame,
):
    """
    Adds a recipe to the given dataframe and persists it to CSV.
    """
    dataframe = dataframe.sort_values(by=["TotalTimeInMins"])

    # join lists into strings if needed
    ingredients_str = ", ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)
    cleaned_ingredients_str = ", ".join(cleaned_ingredients) if isinstance(cleaned_ingredients, list) else str(cleaned_ingredients)

    new_recipe = pd.DataFrame(
        [
            [
                recipe_name,
                ingredients_str,
                cooking_time,
                cuisine,
                translated_instructions,
                cleaned_ingredients_str,
                len(cleaned_ingredients),
            ]
        ],
        columns=dataframe.columns,
    )

    dataframe = pd.concat([dataframe, new_recipe], ignore_index=True)
    dataframe = update_dataframe(dataframe)
    dataframe.to_csv(CSV_FILE, index=False)


@router.get("/chefbot/recipes_by_cuisine", tags=["chefbot"])
def get_recipes_with_cuisine(cuisine: Optional[str] = None):
    """
    Retrieves recipes with a specified cuisine, or returns the set of all cuisines.

    Args:
        cuisine (str, optional): The cuisine to filter the recipes by.

    Returns:
        dict: {index: recipe_name} if cuisine given,
        or list of cuisines if no cuisine provided.
    """
    dataframe = pd.read_csv(CSV_FILE)
    dataframe = dataframe.sort_values(by=["Ingredient-count"])
    dataframe.dropna(subset=["Cuisine", "TranslatedRecipeName"], inplace=True)

    if cuisine and cuisine.strip():
        cuisine = cuisine.title()
        cuisine_data = dataframe[dataframe["Cuisine"] == cuisine]
        return_dictionary = {
            count: recipe.split(",")[0]
            for count, recipe in enumerate(
                cuisine_data["TranslatedRecipeName"].tolist(), start=1
            )
        }
        if not return_dictionary:
            return {404: f"No recipes found for cuisine '{cuisine}'."}
        return return_dictionary
    else:
        cuisine_set = sorted(set(dataframe["Cuisine"].unique()))
        return {"cuisines": cuisine_set}


def convert_minutes_to_hours(minutes: Union[int, float]) -> int:
    """
    Convert the given number of minutes to full hours.
    """
    try:
        return int(minutes) // 60
    except Exception:
        return 0


def update_category(row):
    """
    Example of a category updater; adjust logic as needed.
    """
    if "Cow" in str(row["TranslatedRecipeName"]):
        return "Non Veg"
    else:
        return "Veg"


def update_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the dataframe by applying the update_category function.
    """
    dataframe["Category"] = dataframe.apply(update_category, axis=1)
    return dataframe


if __name__ == "__main__":
    from pprint import pprint
    pprint(fetch_the_menu(dish="Shakshuka"))
