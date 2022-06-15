# Deputweet
Deputweet tweet each time a french member of the Assemblé Nationale votes based on the data available [here](https://data.assemblee-nationale.fr)

# How to use it ?
You have two choices to run this script for your deputy :

## 1 Clone repository
- You can clone this repo and modify the twitter_crendtial.csv file to put the Twitter API credentials of the account you've created for the deputy you want to track.
You'll need to know the code of your deputy (PAXXXXXX), which can be found in the file available [here](https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice)
- You then add a cronjob to call regularly main.py

## 2 Give me Twitter API credentials
 Since there is almost 600 french deputy, I can't create all those Twitter accounts on my own. But I can host and run the script for you as long as you give me all required Twitter API credentials. **Do not give me your personnal credentials, nor the login and password of the account you've created**. The process to retrieve your API credentials is detailed right below
 
 # How to retrive Twitter API credentials ?
 - Create a new Twitter account for the deputy you want to track (with a dedicated email)
 - Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
 - Fill in the form (you'll need a phone number to verify the account)
 - You'll be asked to verify your developer account and then redirected to a page asking for an App name.
 - Choose a name (Deputweet_LastNameDeputy_FirstNameDeputy for instance but you can be more creative, name doesn't matter) and click "Get Keys"
 - Save API Key, API Key Secret and Bearer Token. You'll be able to regenerate them later if you loose them
 - Click "Skip to dashboard"
 - On the left of the dashboard go to Project & App -> NameOfYourApp
 - Set up AAuth1.0 with Read and Write authorizations (put random domain names in required fields)
 - Then, on the top of the screen click "Keys and tokens" and generate "Access Token and Secret", save them too !
 
 Here you go ! You've made it. Your twitter account is all set up now.
 
 Feel free to re-use, modify or improve the code and personalize tweet message !
 
