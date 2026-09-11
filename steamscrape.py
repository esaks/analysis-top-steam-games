# Scrape steam data into a csv file for analysis

#Create virtual environment for importing modules for this project to avoid conflicting python and dependency versions
# Created virtual environment for this project: emily@LJX7J22WQP virtualenvs % python3 -m venv venv_steamscrape. 
# If you name it .venv and put it in the project folder, VSCode should automatically use it, but if you use cloud storage you might need to keep the virtual environments in a separate place. In this case, I created new folder in home directory: emily@LJX7J22WQP ~ % mkdir ~/virtualenvs 
# Activate: Navigate to the project folder and use source .venv/bin/activate. You should see your virtual environment now in parentheses.
# Install packages: Now run pip install packagename. It should be found under lib, python version, site packages
# DO NOT use global install like pip3 install...
# Ensure VSCode is using the correct interpreter by checking in the bottom right
# May need to alter JSON settings Ctrl + Shift+P if using cloud storage and putting environments in separate folder

# standard module imports
from bs4 import BeautifulSoup 
import csv
import os
import statistics
import time
import re

# third-party imports
import requests #module for opening arbitrary resources by URL
import numpy as np
import pandas as pd


# Retrieve appids for top 100 most popular games 
# Note: To find the correct part of the text, you can explore the webpage and right click on the elements you want and inspect them
# Search for specific patterns appearing and try them
# In this case, we are probably looking for a hyperlink or <a> referring to a link that appears and contains appid
# We can start with soup.find_all("a") to look through all of a class with game_links = soup.find_all(r"a")
# Here we do see the "search_result_row" appear
# Next we can narrow down to a more specific pattern and use soup.select until we get it right
games = []
for start in range(0, 100, 50):
    url = f"https://store.steampowered.com/search/?filter=topsellers&start={start}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    games.extend(soup.select(".search_result_row"))

print(len(games)) # prints length of total items retrieved
# Can tell page size or how many results per page print(len(soup.select(".search_result_row")))
# Must find the pagination  signal (start, page, offset, cursor, etc.), then get the page size to find the step number for range
# Can inspect the page to determine pagination signal

rows = []
for row in games:
    appid = row['data-ds-appid']
    rows.append({"appid": appid})
    #print(f"ID: {appid} | URL: {href}")

# Create empty list for data 
final_data = []

# Append data
for row in rows: 
    appid = row['appid']
    game_entry = {"appid": appid}

    # Retrieve app details
    app_details_req = requests.get(
        f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en" #added us and english to the end to get correct prices
    ).json()
    entry =app_details_req.get(str(appid), {})
    if not entry.get("success"): # it not a success end this iteration
        continue

    game_data = entry.get("data") #if a success, add the data to game_data

    if game_data is None:
        continue

# Add app details information
    game_entry["name"] = game_data.get("name")
    game_entry["type"] = game_data.get("type")
    game_entry["mac_available"] = (
            game_data.get("platforms", {}).get("mac", False)
            if game_data.get("platforms")
            else False
        )
    game_entry["windows_available"] = (
            game_data.get("platforms", {}).get("windows", False)
            if game_data.get("platforms")
            else False
        )
    game_entry["linux_available"] = (
            game_data.get("platforms", {}).get("linux", False)
            if game_data.get("platforms")
            else False
        )
    game_entry["release_date"] = (
            game_data.get("release_date", {}).get("date")
            if game_data.get("release_date")
            else None
        )
    game_entry["publishers"] = game_data.get("publishers")
    game_entry["developers"] = game_data.get("developers")
    game_entry["genres"] = (
            ",".join([g["description"] for g in game_data.get("genres", [])])
            if game_data.get("genres")
            else None
        )
    game_entry["categories"] = (
            ",".join([g["description"] for g in game_data.get("categories", [])])
            if game_data.get("categories")
            else None
        )
    game_entry["price_initial"] = game_data.get("price_overview", {}).get(
            "initial"
        )
    game_entry["description"] = game_data.get("short_description")
    game_entry["recommendation_total"] = (
            game_data.get("recommendations", {}).get("total")
            if game_data.get("recommendations")
            else None
        )
    game_entry["metacritic"] = (
            game_data.get("metacritic", {}).get("score")
            if game_data.get("metacritic")
            else None
        )
    game_entry["num_achievements"] = (
            game_data.get("achievements", {}).get("total")
            if game_data.get("achievements")
            else None
        )
    time.sleep(1.5)  # Respectful delay between API targets


    # Retrieve and append user review information
    try:
        response = requests.get(f"https://store.steampowered.com/appreviews/{appid}?json=1")
        response.raise_for_status() #raise an exception if it fails

        user_review_req = response.json()

        query_summary = user_review_req.get("query_summary", {})

        print("Successful request!")
        print(f"Status Code: {response.status_code}")
        #print(query_summary)

        game_entry["review_score"] = query_summary.get("review_score")
        game_entry["review_score_desc"] = query_summary.get("review_score_desc")
        game_entry["total_positive"] = query_summary.get("total_positive")
        game_entry["total_negative"] = query_summary.get("total_negative")
        game_entry["total_reviews"] = query_summary.get("total_reviews")
        
        time.sleep(1.5)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    final_data.append(game_entry)
    time.sleep(1.5)

# Change from dictionary to data frame
top100_games_df = pd.DataFrame(final_data)

# Save to csv file
top100_games_df.to_csv("/Users/emily/Library/CloudStorage/Box-Box/Coding/Steam analysis with basic web scraping in Python/top100games.csv", index=False)

# Resources
# ChatGPT
# Resource: https://nik-davis.github.io/posts/2019/steam-data-collection/
# ResourcE: https://medium.com/codex/scraping-information-of-all-games-from-steam-with-python-6e44eb01a299


