from flask import Flask, Blueprint, render_template, redirect, url_for
from .helper_functions import fetch_and_save_data, format_query_price_information
from .forms import SearchForm
from .database import db, SavedData, GeneralQueryData, SingleItem
import matplotlib
import matplotlib.pyplot as plt
import os


app = Flask(__name__)
blueprint_main = Blueprint('blueprint_main', __name__,
                           template_folder="templates")
matplotlib.use('Agg')


@blueprint_main.route("/", methods=["GET", "POST"])
def main():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        search_parameter = search_form.search_parameter.data
        delivery_destination = search_form.delivery_destination.data

        free_shipping = int(search_form.free_shipping.data[0]) if len(
            search_form.free_shipping.data) != 0 else None
        limit = search_form.limit.data if search_form.limit.data != None else 50
        market = search_form.market.data if search_form.market.data != None else "EBAY_US"
        sort_by = search_form.sort_by.data if search_form.sort_by.data != "None" else None
        min_price = search_form.price_filter_min.data
        max_price = search_form.price_filter_max.data
        conditions_id_list = search_form.condition.data
        currency = search_form.currency.data if search_form.currency.data != "None" else None

        fetch_and_save_data(search_parameter=search_parameter, delivery_destination=delivery_destination, free_shipping=free_shipping, limit=limit,
                            market=market, sort_by=sort_by, min_price=min_price, max_price=max_price, conditions_id_list=conditions_id_list, currency=currency)

        return redirect(url_for("blueprint_main.display_items"))

    return render_template("index.html", search_form=search_form)


@blueprint_main.route("/display-items", methods=["GET", "POST"])
def display_items():
    data = SavedData.query.all()
    last_search = data[-1]
    display_format = SavedData.query.filter_by(id=last_search.id).first()

    return render_template("items.html", display_list=display_format)


@blueprint_main.route("/generate-graph", methods=["GET", "POST"])
def generate_graph():
    save_path = os.path.abspath(os.path.join("main", "static", "data.png"))

    data = SavedData.query.all()

    last_query = data[-1]
    general_query_data = last_query.general_query_data
    search_parameter_name = last_query.search_parameter

    matplot_display_list = []
    market_names = []
    for item in general_query_data:
        price_list = [item.price for item in item.items]
        market_names.append(f"{item.market} ({item.currency})")
        matplot_display_list.append(price_list)

    plt.figure(figsize=(12, 8))
    plt.ylabel("Price")
    plt.boxplot(matplot_display_list, label=search_parameter_name,
                tick_labels=market_names)
    plt.xticks(rotation=45, fontsize=8)
    plt.subplots_adjust(bottom=0.30)
    plt.legend([search_parameter_name, ])
    plt.savefig(save_path, bbox_inches='tight')
    plt.clf()

    return render_template("graph.html")


@blueprint_main.route("/delete-item/<int:id>", methods=["GET", "POST"])
def delete_item(id: int):
    item = SingleItem.query.filter_by(id=id).first()
    db.session.delete(item)
    general_data = GeneralQueryData.query.filter_by(id=item.parent_id).first()
    items_list = general_data.items
    price_list = [item.price for item in items_list]
    average_price, median_price, min_price, max_price = format_query_price_information(
        price_list)
    general_data.average_price = average_price
    general_data.min_price = min_price
    general_data.max_price = max_price
    general_data.median_price = median_price

    db.session.commit()

    return redirect(url_for("blueprint_main.display_items"))


@blueprint_main.route("/about", methods=["GET"])
def about_page():

    return render_template("about.html")
