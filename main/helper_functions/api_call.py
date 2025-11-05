from ..database import db, SavedData
import json
import asyncio
import aiohttp
from ..env_config import EBAY_BROWSE_API, EXCHANGE_RATE_API_KEY
from .converters import str_to_list_converter_for_market, convert_market_id_to_country_name
from .parameters_and_headers_for_request import paramaters_and_headers_for_request
from .format_data import format_general_query_data, conditions_list_formater


async def get_data(search_parameter: dict, headers_data: dict, init_currency_conversion: bool, session: aiohttp.client.ClientSession) -> dict:
    """
    Gets listings data from Ebay API and exchange rates from ExchangeRateAPI, which is used to convert to specified currency if needed.  
    """
    try:
        print("getting data...")
        items = await session.get(url=EBAY_BROWSE_API, params=search_parameter, headers=headers_data)
        items_response = await items.json()
        return_dict = {}
        print("got items.")

        if init_currency_conversion != None:
            currency = items_response["itemSummaries"][0]["price"]["currency"]
            exhcnage_api_url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{currency}'

            exchange_rates = await session.get(url=exhcnage_api_url)
            exchange_rates_response = await exchange_rates.json()
            print("got exchange rates.")

            return_dict = {"items": items_response,
                           "exchange_rates": exchange_rates_response}
        else:
            return_dict = {"items": items_response}

        return return_dict

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


async def gather_data(parameters_and_headers_list: list, init_currency_conversion: str | None) -> list:
    """
    Creates one or more asynchronous calls based on how many markets were selected.   
    """

    async with aiohttp.ClientSession() as session:
        tasks = [get_data(search_parameter=item[0], headers_data=item[1],
                          init_currency_conversion=init_currency_conversion, session=session) for item in parameters_and_headers_list]
        return await asyncio.gather(*tasks)


def fetch_and_save_data(market: list,
                        free_shipping: int,
                        delivery_destination: str,
                        search_parameter: str,
                        limit: int,
                        sort_by: str,
                        min_price: int,
                        max_price: int,
                        conditions_id_list: list,
                        currency: str) -> None:
    """
    This function takes information from a form and uses it to make API calls.
    """

    parameters_and_headers_list = []
    market_list = str_to_list_converter_for_market(market)
    formated_conditions_id_list = conditions_list_formater(
        str(conditions_id_list))
    market_names = convert_market_id_to_country_name(market_list=market_list)

    for market in market_list:

        parameters_and_headers = paramaters_and_headers_for_request(search_parameter=search_parameter,
                                                                    limit=limit,
                                                                    market=market,
                                                                    sort_by=sort_by,
                                                                    min_price=min_price,
                                                                    max_price=max_price,
                                                                    conditions_id_list=formated_conditions_id_list,
                                                                    delivery_destination=delivery_destination,
                                                                    max_delivery_cost=free_shipping,
                                                                    currency=currency
                                                                    )
        parameters_and_headers_list.append(list(parameters_and_headers))

    data = asyncio.run(gather_data(
        parameters_and_headers_list, init_currency_conversion=currency))
    formated_data = json.dumps(data, indent=4)

    save_data = SavedData(search_parameter=search_parameter,
                          data=formated_data,
                          market_list=str(market)
                          )
    db.session.add(save_data)
    db.session.commit()

    format_general_query_data(
        market_names=market_names, currency=currency, sort_by=sort_by)
