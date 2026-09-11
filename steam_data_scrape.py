
# import modules
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd


# Retrieve appids for top 100 most popular games 
# .search_result_row contains the appid information
games = []
for start in range(0, 100, 50):
    url = f"https://store.steampowered.com/search/?filter=topsellers&start={start}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    games.extend(soup.select(".search_result_row"))

print(len(games)) # prints length of total items retrieved

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
    time.sleep(1.5)  # Delay between API calls


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
top100_games_df.to_csv("data/top100games.csv", index=False)