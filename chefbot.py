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
    """Fetch the menu of dishes we have available.

    Args:
        dish (str): Name of dish you want to make. Ex: Idli, upma, roti, chappati, pasta, pizza, rajma, daal.
    """
    headers = {
    'accept': 'application/json',
    }
    params = {
        'dish': dish,
    }
    response = requests.get('http://192.168.0.36:6969/chefbot/get_dishes', params=params, headers=headers)
    pprint(response.content.decode("utf-8"))

def fetch_recipe(dish: str, index: int):
    """Fetch the recipe we want to make.

    Args:
        dish (str): Name of dish you want to make. Ex: Idli, upma, roti, chappati, pasta, pizza, rajma, daal.
        index (int): The index number of the dish we want to make from the fetch the menu endpoint.
    """
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
    """Download the recipe locally.

    Args:
        dish (str): Name of dish you want to make. Ex: Idli, upma, roti, chappati, pasta, pizza, rajma, daal.
        index (int): The index number of the dish we want to make from the fetch the menu endpoint.
        favourite (bool, optional): If we want to make the dish a favourite so we can make it again and again and thus not delete it when we clear the table and delete all the files in the recipes folder. Defaults to False.
    """
    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
    }
    params = {
        'dish': dish,
        'index_number': index,
    }

    response = requests.post('http://192.168.0.36:6969/chefbot/download_recipe', params=params, headers=headers)
    if len(response > 1):
        print(response[1].text)
        with open(markdown_file_path+f"{response[0]}.md", "w") as file:
            file.write(response[1].text)
        if favourite:
            with open(favourites_folder+f"{response[0]}.md", "w") as file:
                file.write(response[1].text)
    else:
        print(response)

def cook(dish: str, index: int):
    """The magnum opus of this script. the robot arm will go through the recipe of the dish we want to make and recognize the ingedrients and cook it for us. Then clear the table and delete the files in the recpies folder.

    Args:
        dish (str): Name of dish you want to make. Ex: Idli, upma, roti, chappati, pasta, pizza, rajma, daal.
        index (int): The index number of the dish we want to make from the fetch the menu endpoint.
    """
    recipe = fetch_recipe(dish=dish, index=index)
    clear_the_table()

def clear_the_table():
    """Delete the files in the recipes folder.
    """
    for file in os.listdir(markdown_file_path):
        os.remove(os.path.join(markdown_file_path, file))

download_recipie(args.dishname, True)
clear_the_table()