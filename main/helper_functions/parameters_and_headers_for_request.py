from requests.auth import HTTPBasicAuth
import requests
from ..env_config import CLIENT_ID, CLIENT_SECRET, GET_TOKEN_LINK, SCOPE


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


def paramaters_and_headers_for_request(search_parameter: str,
                                       max_delivery_cost: int,
                                       limit: int, sort_by: str,
                                       min_price: int, max_price: int,
                                       market: str,
                                       conditions_id_list: list,
                                       delivery_destination: str,
                                       currency: str
                                       ) -> dict:
    """
    Formatting parameters and data for requests.
    """

    token = generate_token()

    parameters = {
        "q": search_parameter
    }

    filter_list = []

    if currency == None:
        currency = market[1]
    if limit != None:
        parameters["limit"] = limit
    if sort_by != None:
        parameters["sort"] = sort_by
    if min_price != None and max_price != None:
        filter_list.append(
            f"price:[{min_price}..{max_price}],priceCurrency:{currency}")
    if min_price != None and max_price == None:
        filter_list.append(f"price:[{min_price}..],priceCurrency:{currency}")
    if max_price != None and min_price == None:
        filter_list.append(f"price:[..{max_price}],priceCurrency:{currency}")
    if max_delivery_cost != None:
        filter_list.append(f"maxDeliveryCost:{max_delivery_cost}")
    if conditions_id_list != "{}":
        filter_list.append(f"conditions:{conditions_id_list}")

    if len(filter_list) != 0:
        comma_sepparated_filter_list = ",".join(filter_list)
        parameters["filter"] = comma_sepparated_filter_list

    data = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": market[0],
        "X-EBAY-C-ENDUSERCTX": f"contextualLocation=country={delivery_destination}"
    }

    return parameters, data, market[0]
