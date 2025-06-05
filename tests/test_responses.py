import pytest
from main import create_app, db
from main.database import SavedData
import json
import os

#code coverage command (while in root directory) 'pytest tests --cov-report term-missing --cov=main'.

def create_a_response(client, url: str, search_parameter: str = None, delivery_destination: str = None, free_shipping: int = None, limit: int = None, market: str = None, sort_by: str = None, min_price: int = None, max_price: int = None , conditions_id_list: list = None, currency: str = None):
    
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
    if conditions_id_list:
        data_dict["condition"] = conditions_id_list
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




@pytest.fixture()
def main_app():
    
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    
    with app.app_context():
        db.init_app(app)
        db.create_all()

    yield app

@pytest.fixture()
def client(main_app):
    return main_app.test_client()

def test_request(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Search Parameter" in response.data

def test_search_without_selecting_markets(client, main_app):
    with main_app.app_context():

        response = create_a_response(client=client, 
                                     url="/", 
                                     search_parameter="epiphone electric guitar",
                                     delivery_destination="LT")
        
        assert b'<form method="post" action="/generate-graph" class="inline">' in response.data
        assert response.status_code == 200
        assert SavedData.query.count() == 1

def test_search_with_market(client, main_app):
    with main_app.app_context():
    
        response = create_a_response(client=client, url="/", 
                                     search_parameter="epiphone electric guitar", 
                                     market="['EBAY_GB', 'GBP']",
                                     delivery_destination="LT")
        
        assert response.status_code == 200
        assert b'<form method="post" action="/generate-graph" class="inline">' in response.data
        assert b'<h1>Region: Great Britain</h1>' in response.data
        assert SavedData.query.count() == 1

def test_search_with_several_markets(client, main_app):
    with main_app.app_context():
        response = create_a_response(client=client, url="/", 
                                     search_parameter="epiphone electric guitar", 
                                     market=["['EBAY_DE', 'EUR']", "['EBAY_US', 'USD']"],
                                     delivery_destination="LT")
        
        assert response.status_code == 200
        assert b'<form method="post" action="/generate-graph" class="inline">' in response.data
        assert b'<h1>Region: Germany</h1>' in response.data
        assert b'<h1>Region: USA</h1>' in response.data
        assert SavedData.query.count() == 1

def test_delete_items(client, main_app):
    with main_app.app_context():
        response = create_a_response(client=client, url="/", 
                                     search_parameter="epiphone electric guitar", 
                                     market="['EBAY_GB', 'GBP']",
                                     delivery_destination="LT")
        
        
        assert response.status_code == 200
        last_search = SavedData.query.first()
        items = last_search.general_query_data[0].items

        assert len(items) == 50
        assert items[0].id == 1
        client.post("/delete-item/1")
        query_after_delete = SavedData.query.first()
        items_after_delete = query_after_delete.general_query_data[0].items
        assert len(items_after_delete) == 49
        assert items_after_delete[0].id == 2


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
                                     search_parameter="epiphone electric guitar", 
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
        response = create_a_response(client=client, url="/", 
                                     search_parameter="epiphone electric guitar", 
                                     market="['EBAY_US', 'USD']",
                                     min_price=300,
                                     sort_by="price",
                                     delivery_destination="LT",
                                     conditions_id_list=conditions_id_list_input
                                     )

        # data = SavedData.query.all()
        # last_search = data[-1]
        
        last_search = get_last_search()
        formated_last_search = json.loads(last_search.data)

       
        for item in formated_last_search:
            if item != None:
                condition_id_list = [item_in_item_summaries["conditionId"] for item_in_item_summaries in item["items"]["itemSummaries"]]
                print(condition_id_list)
                for condition_id in condition_id_list:
                    assert condition_id in conditions_id_list_input


def test_api_call_with_max_delivery(client, main_app):
    with main_app.app_context():
        response = create_a_response(client=client, url="/", 
                                     search_parameter="epiphone electric guitar", 
                                     market="['EBAY_US', 'USD']",
                                     delivery_destination="LT",
                                     free_shipping="0"
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
        
        path_to_generated_image = os.path.abspath(os.path.join(__file__ ,"../..", "main", "static", "data.png"))
        assert response_2.status_code == 200
        assert os.path.exists(path_to_generated_image)
       



        


        
        
        




        
    