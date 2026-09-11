# import libraries 
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler #pip install scikit-learn
import numpy as np

# Read in data
data = pd.read_csv('data/top100games.csv')

## Descriptives
# View data
print(data.head()) #View first rows and columns
print(data.describe()) #Descriptive statistics mean, std, min, max, quartiles
print(data.info()) # Gives all columns, null counts and types

# Cleaning - drop games that are not type = game
data = data[data['type'] == "game"] 
#print(len(data)) #98, drops 2

# What are the most popular game genres?
all_genres = {}
for text in data['genres']:
    genre_labels = str(text).split(",") #return a list of each separate genre
    for item in genre_labels:
        if item not in all_genres:
            all_genres[item] = 1
        else:
            all_genres[item] += 1

genre_df = pd.DataFrame.from_dict(all_genres.items())
genre_df.columns = ['Genre', 'Count']
genre_df_sorted = genre_df.sort_values(by=['Count'], inplace=False, ascending=False) #sort highest to lowest counts
print(genre_df_sorted) 

# Look at overall review sentiment counts
print(data['review_score_desc'].value_counts()) #Sentiment leans positive

# What percent of games have mac available? 
mac_games = data.query('mac_available == True', inplace=False) #prints data frame with only those games that can be played on mac
#print(len(mac_games)) #number of mac games = 20
#print(len(mac_games)/len(data)) # percent that are mac games 20%

# What is the price of each game in dollars and cents? (alter column)
def cents_to_dollars(cents):
    return cents/100
data.price_initial = data.price_initial.apply(cents_to_dollars)
#print(data.price_initial[0:20])

# Crosstabs - price ranges by review sentiment
print(pd.crosstab(index=data["review_score_desc"], columns=pd.cut(data["price_initial"], bins=[0,20,40,60,80,100,120, float("inf")]), margins=True, dropna=True, normalize="columns"))

# Visualize distribution of prices (histogram)
plt.style.use('seaborn-v0_8-pastel') # set styling theme
fig1, ax=plt.subplots() # create the canvas with fig1 representing the entire file image
data["price_initial"].plot.hist(bins=5) # make histogram using pandas
ax.set(title="Top 100 Games Prices", xlabel="Prices", ylabel="Frequency") #customize with plot
plt.show() #display plot

## Variable construction
# Create new variable just listing the rank
data["rank"] = list(range(1,len(data)+1))
#print(data["rank"])

# Create release year (new column)
def retrieve_year(release_date):
    i = release_date.index(",")
    return int(release_date[i+2:])
data["release_year"] = data.release_date.apply(retrieve_year)
#print(data['release_year'].head())

# Create a scatterplot of year and number of recommendations
fig2, ax= plt.subplots()
data.plot(kind="scatter", x="release_year", y="recommendation_total", ax=ax)
ax.set(title="Top 100 Games Recommendations By Release Year", xlabel="Year", ylabel="Recommendations") #customize with plot
ax.ticklabel_format(axis='y', useOffset=False, style='plain') # to prevent the scientific notation multiplier on the y axis
plt.show()

# Create primary genre as the first genre listed (new column)
def get_first_genre(genres):
    genre_list = str(genres).split(",")
    return genre_list[0]
data["primary_genre"] =  data.genres.apply(get_first_genre)
#print(data["primary_genre"].value_counts()) # examine to address suggestion to collapse low counts into an "other" category
primary_genre_data = data["primary_genre"].value_counts()
def check_counts(row):
    if primary_genre_data[row] < 5:
        return "Other"
    else:
        return row
data["primary_genre"] = data.primary_genre.apply(check_counts) # if any primary genre has less than 5 in the top 100, collapse into an "other" category
#print(data["primary_genre"].value_counts())

# Create mac-only variable
def is_mac_only(row):
    if row["mac_available"] == True and row["windows_available"] == False and row["linux_available"] == False:
        return True
    else:
        return False
data["mac_only"] = data.apply(is_mac_only, axis=1)
print(data['mac_only'].value_counts()) # Note that none of the top 100 games are mac-only

# What percent of reviews were positive? (add new column)
data["percent_pos_reviews"] = data["total_positive"]/data["total_reviews"]
#print(data["percent_pos_reviews"])

## Statistics
# Correlation between release year and price, excludes NA values
print(f"Correlation release year by price: {data['release_year'].corr(data['price_initial'], method='pearson'):.2f}")

# Correlation between release year and total recommendations
print(f"Correlation release year by total recommendations: {data['release_year'].corr(data['recommendation_total'], method='pearson'):.2f}")

# Do metacritic scores correlate with steam scores?
print(f"Correlation metacritic by steam scores: {data['metacritic'].corr(data['review_score'], method='pearson'):.2f}")

# Regression - Predict total recommendations from rank, release year
# Test Assumptions
# Fit the model
Y=data['recommendation_total']
X=data[["rank", "release_year","percent_pos_reviews", "review_score"]]
X = sm.add_constant(X)
mod1 = sm.OLS(Y, X, missing="drop")
print(mod1.fit())
print(mod1.fit().summary())

# Plot residuals - heteroskedasticity
d ={
    "X_actual":data["rank"],
    "Y_actual":data['recommendation_total']
}
df1 = pd.DataFrame(d)
df1["Y_predicted"] = mod1.fit().predict(X)
df1["Residuals"] = df1["Y_actual"] - df1["Y_predicted"]
ax = df1.plot.scatter(x="Y_predicted", y="Residuals")
ax.axhline(0, color='red')
plt.title("Residuals vs. Predicted values")
plt.xlabel("Predicted values")
plt.ylabel("Residuals")
plt.show()

# Multicollinearity
X_data = data[["rank", "release_year","percent_pos_reviews", "review_score"]]
corr_mat = X_data.corr()
print(corr_mat) # correlation matrix
X_data = X_data.dropna()
X_data = sm.add_constant(X_data) # Add a constant to the model (intercept)
vif_data = pd.DataFrame()
vif_data["feature"] = X_data.columns
vif_data["VIF"] = [variance_inflation_factor(X_data.values, i) for i in range(len(X_data.columns))] # Pass the index of each predictor to the variancE_inflation_factor function and store results in the data frame
print(vif_data) #VIF
# percent positive reviews and review_score are multicollinear because one is actually used to calculate the other according to Steam

# QQ Plot - look at what might be causing kurtosis and high condition number
fig3 = sm.qqplot(mod1.fit().resid)
plt.show() # outlier found
#print(data[["rank", "release_year", "review_score", "percent_pos_reviews", "recommendation_total"]].describe()) #Descriptive statistics mean, std, min, max, quartiles

# Investigate and remove outlier
#outlier_row = data.loc[data['recommendation_total'] == max(data['recommendation_total'])]
#print(outlier_row)
#data = data[data["recommendation_total"] != max(data['recommendation_total'])]

# Log transform to keep the outlier (better for handling meaningful outliers)
# Also can help to address distributional violations
data['recommendation_total'] = np.log(data['recommendation_total'])

# Re-fit models dropping one of the multicollinear predictors
Y2=data['recommendation_total']
X2=data[["rank", "release_year","review_score"]]
X2 = sm.add_constant(X2)
mod2 = sm.OLS(Y2, X2, missing="drop")
print(mod2.fit())
print(mod2.fit().summary()) #kurtosis is reduced. High condition number likely due to scaling differences

# Try standardizing the data (to address differences in scale)
data_to_standardize = data[["rank", "release_year", "review_score", "percent_pos_reviews", "recommendation_total"]]
sc = StandardScaler()
scaled = sc.fit_transform(data_to_standardize)
standardized_data = pd.DataFrame(scaled, columns=data_to_standardize.columns)
#print(standardized_data)

# Re-fit models with standardized data
Y3=standardized_data['recommendation_total']
X3=standardized_data[["rank", "release_year","review_score"]]
X3 = sm.add_constant(X3)
mod3 = sm.OLS(Y3, X3, missing="drop")
print(mod3.fit())
print(mod3.fit().summary()) #Successfully got rid of condition error

# Genre differences in recommendation totals, grouped means and regression
mean_genre_recommendations = data.groupby("primary_genre")["recommendation_total"].mean()
print("Average Recommendations by genre:\n", mean_genre_recommendations) 

# Genre differences in review score
mean_genre_reviewscores = data.groupby("primary_genre")["review_score"].mean()
print("Average Review Scores by genre:\n", mean_genre_reviewscores) 

# Genre differences in rank
mean_genre_rank = data.groupby("primary_genre")["rank"].mean()
print("Rank Average by genre:\n", mean_genre_rank) 

# Question: How is game quality (review_score) predicted by release_year, rank, whether the game is for mac and the genre?
# Dummy coding categorical variables
data_dummy_coded = data[["primary_genre", "mac_available"]].copy()
df_dummy = pd.get_dummies(data_dummy_coded, columns=["primary_genre", "mac_available"], drop_first=True, dtype="int")
#print(df_dummy)

data_to_standardize = pd.concat([data[["rank", "release_year", "review_score"]], df_dummy], axis=1)
sc = StandardScaler()
scaled = sc.fit_transform(data_to_standardize)
standardized_data = pd.DataFrame(scaled, columns=data_to_standardize.columns)
Y4=standardized_data['review_score']
X4= standardized_data.drop(columns='review_score') #all columns that aren't review score
X4 = sm.add_constant(X4)

review_score_mod = sm.OLS(Y4, X4, missing="drop")
print(review_score_mod.fit())
print(review_score_mod.fit().summary())
