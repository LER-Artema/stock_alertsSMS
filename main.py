import datetime
import requests
from twilio.rest import Client
import os

# ----Stock_API----
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
APPID_KEY = os.environ.get('APPID_KEY')

# ----News_API-----
NEWS_APPID_KEY = os.environ.get('NEWS_APPID_KEY')

# ----Twillio_API----
account_sid = "AC37076814600b7630646342bf21502bf3"
auth_token = "8bb6dc5db6682418700cf56715c47c09"
client = Client(account_sid, auth_token)

# ----Dates----
year = datetime.datetime.now().year
month = datetime.datetime.now().month
yesterday = datetime.datetime.now().day - 1
day_before_yesterday = yesterday - 2

url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSLA&apikey=21WD9OC39RXJUZN2'
r = requests.get(url)
data = r.json()["Time Series (Daily)"]

# -----process to generate a valid key for the date key in the api response
if month < 10 and yesterday < 10:
    yesterday = data[f"{year}-0{month}-0{yesterday}"]
    day_before_yesterday = data[f"{year}-0{month}-0{day_before_yesterday}"]
elif month < 10:
    yesterday = data[f"{year}-0{month}-{yesterday}"]
    day_before_yesterday = data[f"{year}-0{month}-{day_before_yesterday}"]
elif yesterday < 10:
    yesterday = data[f"{year}-{month}-0{yesterday}"]
    day_before_yesterday = data[f"{year}-{month}-0{day_before_yesterday}"]
# ----console response-----
day_before_yesterday = float(day_before_yesterday['4. close'])
yesterday = float(yesterday['4. close'])
balance = float(yesterday) - float(day_before_yesterday)
percent = balance / (day_before_yesterday / 100)
print(percent)
state_stocks = ""
if balance < 0:
    state_stocks = "fall"
if balance > 0:
    state_stocks = "increase"
print("The day before yesterday balance is:", day_before_yesterday)
print("The yesterday balance is:", yesterday)
print("The total balance is:", balance.__round__(3))
# ----evaluation of the results----

lose_limit = (balance / 100) * 5
if balance < lose_limit or balance > lose_limit:
    parameters = {
        "q": "TSLA",
        "from": f"{year}-{month}-{yesterday}",
        "sortBy": "all",
        "language": "en",
        "apiKey": NEWS_APPID_KEY
    }
    news = requests.get("https://newsapi.org/v2/top-headlines?", params=parameters) \
        .json()
    if news["totalResults"] == 0:
        message = client.messages \
            .create(
                body=f"---------------------------"
                     f"\nThe Tesla Stock has {state_stocks} by {percent.__round__(2)}%\n"
                     f"------------------------------",
                from_='+14154170291',
                to='+525522494955'
            )
    else:
        body_of_sms = ""
        # formating of the date time
        fst_nw = [news[0]["title"], news[0]["description"], news[0]["url"]]
        body_of_sms = body_of_sms + f"{fst_nw[0]} \n {fst_nw[1]} \n {fst_nw[2]}\n\n"
        if len(news) > 1:
            snd_nw = [news[1]["title"], news[1]["url"]]
            body_of_sms = body_of_sms + f"{snd_nw[0]}\n{snd_nw[1]}\n"
            if len(news) > 2:
                thd_nw = [news[2]["title"], news[2]["url"]]
                body_of_sms = body_of_sms + f"{thd_nw[0]}\n{thd_nw[1]}"

        # sending the message
        message = client.messages \
            .create(
                body=f"---------------------------"
                     f"\nThe Tesla Stock has {state_stocks} by {percent.__round__(2)}%\n"
                     f"------------------------------"
                     f""
                     f""
                     f"{body_of_sms}",
                from_='+14154170291',
                to='+525522494955'
                )
