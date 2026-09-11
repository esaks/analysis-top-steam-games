# analysis-top-steam-games
Beginning personal project involving web scraping and analysis of the top 100 selling video games on Steam

## Project Summary
Scrape the current top 100 selling Steam games, compile game details (release year, recommendations, genre, price, etc.) into a CSV file, and analyze the data in Python.

## Purpose
I wanted to teach myself basic web scraping and using the pandas library.

## Results
I ran the code June 17, 2026, so results reflect the top selling games at that time.
* 89 were strictly classified as games (as opposed to other types of products like dlc)
* The most common genres appeared to be Action, Adventure and RPG
* 18 out of the 89 were available for Mac
* There was only a small correlation between release year and price (R=0.18)
* There was a moderate negative correlation between release year and total recommendations (R = -0.37). This suggests that games that have been available longer tend to have more total recommendations, indicating that recommendations are at least partly a function of time.
* There was a small positive correlation between Metacritic ratings and Steam's review score among games with available Metacritic ratings (R = 0.26).
* Recommendations and review scores did not appear to differ substantially between games of different genres, although games of different genres may rank differently within the top 100.
* Regression models predicting total recommendations from rank, release year, and review score, and predicting review score from rank, release year, genre, and Mac availability, did not appear to fit the data well.
