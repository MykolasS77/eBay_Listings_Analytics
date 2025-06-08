from main.database import SavedData


def create_a_response(client, url: str, search_parameter: str = None, delivery_destination: str = None, free_shipping: int = None, limit: int = None, market: str = None, sort_by: str = None, min_price: int = None, max_price: int = None, conditions_list: list = None, currency: str = None):

    data_dict = {}
    if search_parameter:
        data_dict["search_parameter"] = search_parameter
    if limit:
        data_dict["limit"] = limit
    if market:
        data_dict["market"] = market
    if sort_by:
        data_dict["sort_by"] = sort_by
    if min_price:
        data_dict["price_filter_min"] = min_price
    if max_price:
        data_dict["price_filter_max"] = max_price
    if conditions_list:
        data_dict["condition"] = conditions_list
    if delivery_destination:
        data_dict["delivery_destination"] = delivery_destination
    if free_shipping:
        data_dict["free_shipping"] = free_shipping
    if currency:
        data_dict["currency"] = currency

    response = client.post(url, data=data_dict, follow_redirects=True)

    return response


def get_items():
    last_search = SavedData.query.first()
    items = last_search.general_query_data[0].items
    return items


def get_last_search():
    data = SavedData.query.all()
    last_search = data[-1]
    return last_search
