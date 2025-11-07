import json
import statistics
from ..database import db, SavedData, GeneralQueryData, SingleItem
from .converters import convert_to_specified_currency
from ..country_codes import get_country_name_by_id


def format_general_query_data(market_names: list, currency: str, sort_by: str = None) -> None:
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
                                         image_href=item["image"]["imageUrl"] if "image" in item else "",
                                         parent_id=added_item[-1].id,
                                         market=market_names[index],
                                         location=get_country_name_by_id(
                                             item["itemLocation"]["country"])

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


def conditions_list_formater(conditions_id_list: str) -> str:
    """
    Ebay API uses specific format for item conditions filtering (e.g 'filter=conditionIds:{1000|1500}'). 
    This function converts a string representation list of ids into this format. 
    """

    replacements = str.maketrans(
        {"[": "{", "]": "}", ",": "|", "'": "", " ": ""})
    formated_conditions_id_list = conditions_id_list.translate(replacements)

    return formated_conditions_id_list


def get_shipping_price(item: dict) -> float:
    """
    Returns shipping price for one item.
    """

    if "shippingOptions" in item:
        shipping_price = item["shippingOptions"][0]["shippingCost"]["value"]

        return float(shipping_price)
    else:
        return 0
