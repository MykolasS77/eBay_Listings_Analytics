from requests.auth import HTTPBasicAuth
from .forms import MARKET_LIST
from .database import db, SavedData, GeneralQueryData, SingleItem
import requests
import json
import statistics
import asyncio
import aiohttp
from .env_config import CLIENT_ID, CLIENT_SECRET, GET_TOKEN_LINK, SCOPE, EBAY_BROWSE_API, EXCHANGE_RATE_API_KEY


def generate_token() -> str:
    """
    Generates a new token for each API call.
    """

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": SCOPE
    }

    response = requests.post(GET_TOKEN_LINK, auth=HTTPBasicAuth(
        CLIENT_ID, CLIENT_SECRET), headers=headers, data=data)
    response_json = response.json()

    return response_json["access_token"]


def str_to_list_converter_for_market(market_list_string: list) -> list:
    """
    Converts string representation of a list into a true list type.
    """

    if type(market_list_string) == list:
        new_list = [eval(item) for item in market_list_string]
        return new_list


def str_to_list_converter_for_conditions_id_list(conditions_id_list: str) -> str:
    """
    Ebay API uses specific format for item conditions filtering (e.g 'filter=conditionIds:{1000|1500}'). 
    This function converts a string representation list of ids into this format. 
    """
    replacements = str.maketrans(
        {"[": "{", "]": "}", ",": "|", "'": "", " ": ""})
    formated_conditions_id_list = conditions_id_list.translate(replacements)

    return formated_conditions_id_list


def request_parameters_and_headers(search_parameter: str, max_delivery_cost: int, limit: int, sort_by: str, min_price: int, max_price: int, market: str, conditions_id_list: list, delivery_destination: str):
    """
    Formatting parameters and data for requests.
    """
    token = generate_token()

    parameters = {
        "q": search_parameter
    }

    filter_list = []

    if limit != None:
        parameters["limit"] = limit
    if sort_by != None:
        parameters["sort"] = sort_by
    if min_price != None and max_price != None:
        filter_list.append(
            f"price:[{min_price}..{max_price}],priceCurrency:{market[1]}")
    if min_price != None and max_price == None:
        filter_list.append(f"price:[{min_price}..],priceCurrency:{market[1]}")
    if max_price != None and min_price == None:
        filter_list.append(f"price:[..{max_price}],priceCurrency:{market[1]}")
    if max_delivery_cost != None:
        filter_list.append(f"maxDeliveryCost:{max_delivery_cost}")
    if conditions_id_list != "{}":
        filter_list.append(f"conditionIds:{conditions_id_list}")

    if len(filter_list) != 0:
        comma_sepparated_filter_list = ",".join(filter_list)
        parameters["filter"] = comma_sepparated_filter_list

    data = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": market[0],
        "X-EBAY-C-ENDUSERCTX": f"contextualLocation=country={delivery_destination}"
    }

    return parameters, data, market[0]


def convert_market_id_to_country_name(market_list: list) -> list:
    """
    Creating a list with full country names based country id.
    """
    new_list = []
    for index, item in enumerate(MARKET_LIST):
        if item[0] in market_list:
            new_list.append(item[1])
    return new_list


def convert_to_specified_currency(price: int, convert_to_currency: str, exchange_rate_dict: dict):

    exchange_rate = exchange_rate_dict["conversion_rates"][convert_to_currency]

    new_price = round(float(price) * float(exchange_rate), 2)
    return new_price


async def get_data(search_parameter: dict, headers_data: dict, session: aiohttp.client.ClientSession) -> dict:
    """
    Gets listings data from Ebay API and exchange rates from ExchangeRateAPI, which is used to convert to specified currency if needed.  
    """
    try:
        print("getting data...")
        items = await session.get(url=EBAY_BROWSE_API, params=search_parameter, headers=headers_data)
        items_response = await items.json()
        print("got items.")
        currency = items_response["itemSummaries"][0]["price"]["currency"]
        exhcnage_api_url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{currency}'

        exchange_rates = await session.get(url=exhcnage_api_url)
        exchange_rates_response = await exchange_rates.json()
        print("got exchange rates.")

        return_dict = {"items": items_response,
                       "exchange_rates": exchange_rates_response}

        return return_dict

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


async def gather_data(parameters_and_headers_list: list) -> list:
    """
    Creates one or more asynchronous calls based on how many markets were selected.   
    """
    async with aiohttp.ClientSession() as session:
        tasks = [get_data(search_parameter=item[0], headers_data=item[1],
                          session=session) for item in parameters_and_headers_list]
        return await asyncio.gather(*tasks)


def format_query_price_information(items_price_list: list) -> list:
    """
    Calculates average, median, min and max prices for each query.  
    """

    if len(items_price_list) != 0:
        average_price = round(sum(items_price_list) / len(items_price_list), 2)
        median_price = round(statistics.median(items_price_list), 2)
        min_price = min(items_price_list)
        max_price = max(items_price_list)

        return average_price, median_price, min_price, max_price
    else:
        return 0, 0, 0, 0


def get_shipping_price(item: dict) -> float:
    """
    Returns shipping price for one item.
    """
    if "shippingOptions" in item:
        shipping_price = item["shippingOptions"][0]["shippingCost"]["value"]

        return float(shipping_price)
    else:
        return 0


def format_general_query_data(market_names: list, currency: str, sort_by: str = None):
    """
    Saves data from API call into a database.  
    """

    data = SavedData.query.all()
    last_search = data[-1]
    formated_last_search = json.loads(last_search.data)

    for index, data_item in enumerate(formated_last_search):
        if data_item:
            item_summaries = data_item["items"]["itemSummaries"]
            if currency == None:

                items_price_list = [float(item["price"]["value"])
                                    for item in item_summaries]
                item_currency = item_summaries[0]["price"]["currency"]
            else:
                items_price_list = [convert_to_specified_currency(price=float(
                    item["price"]["value"]), convert_to_currency=currency, exchange_rate_dict=data_item["exchange_rates"]) for item in item_summaries]
                item_currency = currency

            average_price, median_price, min_price, max_price = format_query_price_information(
                items_price_list)

            format_data = GeneralQueryData(
                currency=item_currency,
                average_price=average_price,
                min_price=min_price,
                max_price=max_price,
                median_price=median_price,
                market=market_names[index],
                parent_id=last_search.id
            )
            db.session.add(format_data)
            db.session.commit()
            added_item = GeneralQueryData.query.filter_by(
                parent_id=last_search.id).all()
            items_list = []
            for item in item_summaries:

                if currency == None:
                    price = float(item["price"]["value"])
                    shipping_price = get_shipping_price(item)
                    total_price = round(price + shipping_price, 2)
                else:
                    price = convert_to_specified_currency(price=float(
                        item["price"]["value"]), convert_to_currency=currency, exchange_rate_dict=data_item["exchange_rates"])
                    shipping_price = convert_to_specified_currency(price=float(get_shipping_price(
                        item)), convert_to_currency=currency, exchange_rate_dict=data_item["exchange_rates"])
                    total_price = round(price + shipping_price, 2)

                single_item = SingleItem(title=item["title"],
                                         price=price,
                                         shipping_price=shipping_price,
                                         total_price=total_price,
                                         seller=item["seller"]["username"],
                                         condition=item["condition"],
                                         link_to_product=item["itemWebUrl"],
                                         parent_id=added_item[-1].id,
                                         market=market_names[index],

                                         )

                items_list.append(single_item)

            if sort_by == "price":
                sorted_list = sorted(items_list, key=lambda x: x.total_price)
                db.session.add_all(sorted_list)
            if sort_by == "-price":
                sorted_list = sorted(
                    items_list, key=lambda x: x.total_price, reverse=True)
                db.session.add_all(sorted_list)
            if sort_by == None:
                db.session.add_all(items_list)

            db.session.commit()


def fetch_and_save_data(market: list, free_shipping: int, delivery_destination: str, search_parameter: str, limit: int, sort_by: str, min_price: int, max_price: int, conditions_id_list: list, currency: str):
    """
    This function takes information from a form and uses it to make API calls.
    """

    parameters_and_headers_list = []
    market_list = str_to_list_converter_for_market(market)
    formated_conditions_id_list = str_to_list_converter_for_conditions_id_list(
        str(conditions_id_list))
    market_names = convert_market_id_to_country_name(market_list=market_list)

    for market in market_list:

        parameters_and_headers = request_parameters_and_headers(search_parameter=search_parameter,
                                                                limit=limit,
                                                                market=market,
                                                                sort_by=sort_by,
                                                                min_price=min_price,
                                                                max_price=max_price,
                                                                conditions_id_list=formated_conditions_id_list,
                                                                delivery_destination=delivery_destination,
                                                                max_delivery_cost=free_shipping)
        parameters_and_headers_list.append(list(parameters_and_headers))

    data = asyncio.run(gather_data(parameters_and_headers_list))
    formated_data = json.dumps(data, indent=4)

    save_data = SavedData(search_parameter=search_parameter,
                          data=formated_data,
                          market_list=str(market)
                          )
    db.session.add(save_data)
    db.session.commit()

    format_general_query_data(
        market_names=market_names, currency=currency, sort_by=sort_by)
