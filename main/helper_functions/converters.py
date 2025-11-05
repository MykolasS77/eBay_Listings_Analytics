from ..forms import MARKET_LIST


def convert_to_specified_currency(price: int, convert_to_currency: str, exchange_rate_dict: dict) -> float:

    exchange_rate = exchange_rate_dict["conversion_rates"][convert_to_currency]

    new_price = round(float(price) * float(exchange_rate), 2)
    return new_price


def convert_market_id_to_country_name(market_list: list) -> list:
    """
    Creating a list with full country names based country id.
    """

    new_list = []
    for item in MARKET_LIST:
        if item[0] in market_list:
            new_list.append(item[1])

    return new_list


def str_to_list_converter_for_market(market_list_string: list) -> list:
    """
    Converts string representation of a list into a true list type.
    """

    if type(market_list_string) == list:
        new_list = [eval(item) for item in market_list_string]
        return new_list
