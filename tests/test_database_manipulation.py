from main.database import SavedData
from .helper_functions_for_testing import create_a_response, get_items, get_last_search
from .database_fixture import pytest, client, main_app
import os
import json


def test_delete_items(client, main_app):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="epiphone electric guitar",
                                     market="['EBAY_GB', 'GBP']",
                                     limit=2,
                                     delivery_destination="LT")

        assert response.status_code == 200
        last_search = SavedData.query.first()
        items = last_search.general_query_data[0].items

        assert len(items) == 2
        assert items[0].id == 1
        client.post("/delete-item/1")
        query_after_first_delete = SavedData.query.first()
        items_after_first_delete = query_after_first_delete.general_query_data[0].items
        assert len(items_after_first_delete) == 1
        assert items_after_first_delete[0].id == 2
        client.post("/delete-item/2")
        query_after_second_delete = SavedData.query.first()
        items_after_second_delete = query_after_second_delete.general_query_data[0].items
        average_price = query_after_second_delete.general_query_data[0].average_price
        median_price = query_after_second_delete.general_query_data[0].median_price
        max_price = query_after_second_delete.general_query_data[0].max_price
        min_price = query_after_second_delete.general_query_data[0].min_price

        assert len(items_after_second_delete) == 0
        assert average_price == 0
        assert median_price == 0
        assert max_price == 0
        assert min_price == 0


@pytest.mark.parametrize("min_price_input", [300, 400, 200, 100, 500])
def test_min_price(client, main_app, min_price_input):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="epiphone electric guitar",
                                     market="['EBAY_US', 'USD']",
                                     min_price=min_price_input,
                                     delivery_destination="LT"
                                     )

        assert response.status_code == 200

        last_search = SavedData.query.first()

        assert last_search.general_query_data[0].min_price >= min_price_input


@pytest.mark.parametrize("max_price_input", [300, 400, 200, 100, 500])
def test_max_price(client, main_app, max_price_input):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="epiphone electric guitar",
                                     market="['EBAY_US', 'USD']",
                                     max_price=max_price_input,
                                     delivery_destination="LT"
                                     )
        assert response.status_code == 200

        last_search = SavedData.query.first()

        assert last_search.general_query_data[0].max_price <= max_price_input


@pytest.mark.parametrize("min_price_input, max_price_input", [(300, 400), (500, 600), (100, 500)])
def test_min_and_max_price(client, main_app, min_price_input, max_price_input):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="playstation 5 console",
                                     market="['EBAY_US', 'USD']",
                                     min_price=min_price_input,
                                     max_price=max_price_input,
                                     delivery_destination="LT"
                                     )
        assert response.status_code == 200

        last_search = SavedData.query.first()

        assert last_search.general_query_data[0].max_price <= max_price_input
        assert last_search.general_query_data[0].min_price >= min_price_input


@pytest.mark.parametrize("sort_by_parameter", ["price", "-price"])
def test_sort_by(client, main_app, sort_by_parameter):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="Playstation 5 console",
                                     market="['EBAY_US', 'USD']",
                                     sort_by=sort_by_parameter,
                                     delivery_destination="LT",
                                     limit=200
                                     )

        assert response.status_code == 200

        last_search_items = get_items()
        prices = [item.total_price for item in last_search_items]

        if sort_by_parameter == "price":
            sorted_prices = sorted(prices)
            assert prices == sorted_prices
        if sort_by_parameter == "-price":

            sorted_prices = sorted(prices, reverse=True)
            assert prices == sorted_prices


@pytest.mark.parametrize("conditions_id_list_input", [['1000', '3000'], ["7000"], ["1500", "4000", "6000"], ["2750", "5000"]])
def test_api_call_with_conditions(client, main_app, conditions_id_list_input):
    with main_app.app_context():
        create_a_response(client=client, url="/",
                          search_parameter="epiphone electric guitar",
                          market="['EBAY_US', 'USD']",
                          min_price=300,
                          sort_by="price",
                          delivery_destination="LT",
                          conditions_id_list=conditions_id_list_input
                          )

        last_search = get_last_search()
        formated_last_search = json.loads(last_search.data)

        for item in formated_last_search:
            if item != None:
                condition_id_list = [item_in_item_summaries["conditionId"]
                                     for item_in_item_summaries in item["items"]["itemSummaries"]]
                print(condition_id_list)
                for condition_id in condition_id_list:
                    assert condition_id in conditions_id_list_input


def test_api_call_with_max_delivery(client, main_app):
    with main_app.app_context():
        create_a_response(client=client, url="/",
                          search_parameter="epiphone electric guitar",
                          market="['EBAY_US', 'USD']",
                          delivery_destination="LT",
                          free_shipping=True
                          )

        items = get_items()
        for item in items:
            assert item.shipping_price == 0


@pytest.mark.parametrize("currency_input", ["EUR", "CAD", "CHF", "GBP", "HKD", "PLN", "SGD", "USD"])
def test_convert_to_currency(client, main_app, currency_input):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="epiphone electric guitar",
                                     market="['EBAY_US', 'USD']",
                                     currency=currency_input,
                                     delivery_destination="LT",
                                     )

        last_search = get_last_search()

        general_query_data = last_search.general_query_data

        for item in general_query_data:
            assert item.currency == currency_input


def test_graph_generator(client, main_app):
    with main_app.app_context():
        response = create_a_response(client=client,
                                     url="/",
                                     search_parameter="samsung galaxy s22 smartphone",
                                     market="['EBAY_US', 'USD']",
                                     delivery_destination="LT")

        assert response.status_code == 200

        response_2 = create_a_response(client=client,
                                       url="/generate-graph"
                                       )

        path_to_generated_image = os.path.abspath(os.path.join(
            __file__, "../..", "main", "static", "data.png"))
        assert response_2.status_code == 200
        assert os.path.exists(path_to_generated_image)
