
# Ebay Listings Analytics

The main idea of this project was creating a flask web application which lets you query for listings across several Ebay markets and afterwards analyzing the retrieved results. For example, you may search for "Iphone 16 Pro" and retrieve listings from Ebay US, Ebay Germany, Ebay Spain at once, with information on minimum and maximum price, average and median price for the retrieved items in each selected market. With this application you can browse for items and compare prices across several Ebay markets faster and easier.


## Run Locally

To run this app locally you will first need to register for [eBay developers program ](https://developer.ebay.com/api-docs/static/make-a-call.html). It will take about a day until your account gets confirmed. Afterwards you will need to create a production keyset and take note of your client ID and clientSecret which will be needed for .env configuration. 

You will also need to register for [ExchangeRate-API](https://www.exchangerate-api.com/) and get an API key. This should be very straightforward. 

Clone the project

```bash
  git clone https://github.com/MykolasS77/Ebay_Market_Prices_Analytics
```

Go to the project directory

```bash
  cd project-location
```

Create and activate a virtual environment.

```bash
  python -m venv .venv
```

```bash
  source .venv/Scripts/activate
```

Install dependencies

```bash
  pip install flask matplotlib requests statistics asyncio aiohttp flask_wtf wtforms flask_sqlalchemy sqlalchemy pytest dotenv
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`EBAY_BROWSE_API = "https://api.ebay.com/buy/browse/v1/item_summary/search"`

`EBAY_GENERATE_TOKEN = "https://api.ebay.com/identity/v1/oauth2/token"`

`EBAY_SCOPE = "https://api.ebay.com/oauth/api_scope"`

`CLIENT_ID = "Your eBay clientID"`

`CLIENT_SECRET = "Your eBay client secret"`

`EXCHANGE_RATE_API_KEY = "Your ExchangeRate-API Key"`


Start the app by running the "run.py" file.

```bash
  python run.py
```


## Documentation

[eBay Browse API documentation.](https://developer.ebay.com/api-docs/buy/browse/static/overview.html)

[Registration for eBay developers program.](https://developer.ebay.com/api-docs/static/make-a-call.html)

[ExchangeRate-API.](https://www.exchangerate-api.com/)





