import argparse
from pprint import pprint

import pandas as pd

arguments = argparse.ArgumentParser()

arguments.add_argument('-d', '--dishname', required= True, type= str, help= "A general word of what you want to eat. Ex salad, pasta, pizza.")

args = arguments.parse_args()
pd.set_option("display.max_colwidth", None)
csv_file = r"/home/megamind/git/github/personal/chefbot/Modified_Indian_Food_Dataset.csv"
markdown_file_path = "/home/megamind/chefbot/"

def get_dataframe():
    file = pd.read_csv(csv_file)
    return file


def search_dataset(dish: str):
    count = 1
    dish_dictionary = {}
    df = get_dataframe()
    for dishes in df["TranslatedRecipeName"]:
        if dish.title() in dishes:
            dish_dictionary[count] = []
            dish_dictionary[count].append(dishes)
            count += 1
            # with open("found_dishes.md", 'w') as file:
            #     file.write(str(dishes))
    if len(dish_dictionary) > 0:
        print(f"There are {count-1} different {dish} recipies we found! They are:\n")
        pprint(dish_dictionary)
        choice = input("\n\nChoose the number for which we should prepare the order: ")
        chosen_dish = dish_dictionary[int(choice)][0]
        print(f"""You chose to make: {chosen_dish}\n""")
        df_new = df[df["TranslatedRecipeName"] == chosen_dish]
        index = df_new.index[0]
        dictionary = df_new.to_dict()
        with open(
            rf"{markdown_file_path}/{chosen_dish}.md",
            "w",
        ) as file:
            file.write(
                f"""# {chosen_dish}\n\n## Cooking time: {dictionary['TotalTimeInMins'][index]} minutes.\n\n## Ingredients:\n{dictionary['Cleaned-Ingredients'][index]}\n\n## Cooking Instructions:\n{dictionary['TranslatedInstructions'][index]}"""
            )
    else:
        print("Sorry, we don't have what you are looking for!")
search_dataset(args.dishname)
