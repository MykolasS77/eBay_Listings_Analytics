# ebay Listings Analytics

The main idea of this project was creating a flask web application which lets you query for listings across several Ebay markets and afterwards analyzing the retrieved results. For example, you may search for "Iphone 16 Pro" and retrieve listings from Ebay US, Ebay Germany, Ebay Spain at once, with information on minimum and maximum price, average and median price for the retrieved items in each selected market. With this application you can browse for items and compare prices across several Ebay markets faster and easier.

## Run Locally

To run this app locally you will first need to register for [eBay developers program ](https://developer.ebay.com/api-docs/static/make-a-call.html). It will take about a day until your account gets confirmed. Afterwards you will need to create a production keyset and take note of your client ID and clientSecret which will be needed for .env configuration.

You will also need to register for [ExchangeRate-API](https://www.exchangerate-api.com/) and get an API key. This should be very straightforward.

Clone the project

```bash
  git clone https://github.com/MykolasS77/eBay_Listings_Analytics
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

# Search Form Guide

![empty search ](https://github.com/user-attachments/assets/75f30efd-a300-4c38-92b4-478e8ec519f2)

**Search Parameter**: enter a search parameter. Best to include a category name for the item you are searching for, e.g. "Iphone 16 smartphone", "Playstation 5 console", "razer blackshark v2 headphones" etc.

**Items Limit**: enter the amount of items you wish to get in one query.

**Select Delivery Country**: shipping price gets calculated based on selected country.

**Convert To Currency**: converts all of the prices to a single currency. If left unchecked, each market will show the default currency.

**Free Shipping**: mark to only retrieve items with free shipping to selected country.

**Select Markets**: select the eBay markets you wish to get items from.

**Sort By**: sorts items by total price (price + shipping). Best to use this parameter with **Minimum Price** and **Maximum Price** parameters to avoid inaccurate queries.

**Minimum/Maximum Price**: select the Minimum/Maximum price for each query. If used in combination of "Convert To Currency", the items are first retrieved based on the original currency and only afterwards are converted to selected currency.

**Select Conditions**: retrieve items based on selected item conditions.

# Example of filled search form and retrieved items.

![search](https://github.com/user-attachments/assets/0ee4cc43-449a-4d22-a4a7-d14cf1f36daf)

![searched 1](https://github.com/user-attachments/assets/da5d64f1-99f7-4dac-9f91-f5203a583d31)

![searched 2](https://github.com/user-attachments/assets/3d6e3053-ad1c-46eb-b1ed-45b21b0bc29e)

![searched 3](https://github.com/user-attachments/assets/8e6fa0bd-d3eb-4e59-b025-c3c88698a7c1)

# Generate a box plot chart for all items

Click on a button at the top called "Generate a box plot chart for all items" to get a box plot chart for the retrieved items total prices. Before generating a chart, you can use the "Delete" button to remove specific items from the displayed list, in order to get more accurate representation.

![graph](https://github.com/user-attachments/assets/258cc2a0-7912-4f06-9427-24b138f89f36)

# Running tests

To run tests, cd to root of the directory and run "pytest" or "pytest tests --cov-report term-missing --cov=main" in the terminal.

## Documentation

[eBay Browse API documentation.](https://developer.ebay.com/api-docs/buy/browse/static/overview.html)

[Registration for eBay developers program.](https://developer.ebay.com/api-docs/static/make-a-call.html)

[ExchangeRate-API.](https://www.exchangerate-api.com/)
