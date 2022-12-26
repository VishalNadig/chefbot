import argparse
import requests
from pprint import pprint
import os
arguments = argparse.ArgumentParser()

arguments.add_argument('-d', '--dishname', required= True, type= str, help= "A general word of what you want to eat. Ex salad, pasta, pizza.")
arguments.add_argument('-f', '--favorites', type= bool, help= "A general word of what you want to eat. Ex salad, pasta, pizza.")


args = arguments.parse_args()
markdown_file_path = r"/Users/akshathanadig/Downloads/git/chefbot/recipes/"
favourites_folder = r"/Users/akshathanadig/Downloads/git/chefbot/favourite_recipes/"
def fetch_the_menu(dish: str):
    headers = {
    'accept': 'application/json',
    }
    params = {
        'dish': dish,
    }
    response = requests.get('http://192.168.0.36:6969/chefbot/get_dishes', params=params, headers=headers)
    pprint(response.content.decode("utf-8"))

def fetch_recipe(dish: str, index: int):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
    }

    params = {
        'dish': dish,
        'index_number': index,
    }

    response = requests.post('http://192.168.0.36:6969/chefbot/fetch_recipe', params=params, headers=headers)
    pprint(response.text)


def download_recipie(dish: str, index: int, favourite: bool = False):
    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
    }
    params = {
        'dish': dish,
        'index_number': index,
    }

    response = requests.post('http://192.168.0.36:6969/chefbot/download_recipe', params=params, headers=headers)
    print(response.text)
    with open(markdown_file_path+f"{dish}.md", "w") as file:
        file.write(response.text)
    if favourite:
        with open(favourites_folder+f"{dish}.md", "w") as file:
            file.write(response.text)

def cook(dish: str, index: int):
    recipe = fetch_recipe(dish=dish, index=index)
    clear_the_table()

def clear_the_table():
    for file in os.listdir(markdown_file_path):
        os.remove(os.path.join(markdown_file_path, file))

download_recipie(args.dishname, 1)
clear_the_table()