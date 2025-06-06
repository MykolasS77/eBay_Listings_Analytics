from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange
from .country_codes import COUNTRY_CODES


class SelectMultipleFieldCheckbox(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


CURRENCY_LIST = [
    (None, "-----"),
    ("EUR", "Euro"),
    ("CAD", "Canadian dollar"),
    ("CHF", "Swiss franc"),
    ("GBP", "Great Britain pound"),
    ("HKD", "Hong Kong dollar"),
    ("PLN", "Polish zloty"),
    ("SGD", "Singapore dollar"),
    ("USD", "US dollar"),

]

MARKET_LIST = [
    (['EBAY_AT', 'EUR'], 'Austria'),
    (['EBAY_BE', 'EUR'], 'Belgium'),
    (['EBAY_CA', 'CAD'], 'Canada'),
    (['EBAY_CH', 'CHF'], 'Switzerland'),
    (['EBAY_DE', 'EUR'], 'Germany'),
    (['EBAY_ES', 'EUR'], 'Spain'),
    (['EBAY_FR', 'EUR'], 'France'),
    (['EBAY_GB', 'GBP'], 'Great Britain'),
    (['EBAY_HK', "HKD"], 'Hong Kong'),
    (['EBAY_IE', 'EUR'], 'Ireland'),
    (['EBAY_IT', 'EUR'], 'Italy'),
    (['EBAY_NL', 'EUR'], 'Netherlands'),
    (['EBAY_PL', 'PLN'], 'Poland'),
    (['EBAY_SG', 'SGD'], 'Singapore'),
    (['EBAY_US', "USD"], 'USA'),
]

ITEM_CONDITION_LIST = [
    (1000, "New: unopened, unused"),
    (1500, "New: pacaking may be missing or opened"),
    (2750, "Like new: very lightly used"),
    (3000, "Used, excellent condition"),
    (4000, "Used, very good condition"),
    (5000, "Used, good condition"),
    (6000, "Used, acceptable condition"),
    (7000, "For parts or not working"),
]


class SearchForm(FlaskForm):

    search_parameter = StringField('Search Parameter', validators=[
                                   DataRequired()])  # max 100 characters
    delivery_destination = SelectField(
        'Select delivery destination', choices=COUNTRY_CODES, validators=[DataRequired()])
    free_shipping = BooleanField(
        'Free Shipping', validators=[Optional()])
    limit = IntegerField("Items Limit", validators=[
                         Optional(), NumberRange(min=0, max=200)])
    sort_by = SelectField('Sort By', choices=[(
        None, "-----"), ("price", "Price: lowest to highest"), ("-price", "Price: highest to lowest")], validators=[Optional()])
    price_filter_min = IntegerField("Minimum Price", validators=[Optional()])
    price_filter_max = IntegerField("Maximum Price", validators=[Optional()])
    currency = SelectField('Convert to currency',
                           choices=CURRENCY_LIST, validators=[Optional()])
    market = SelectMultipleFieldCheckbox(
        'Select Markets', choices=MARKET_LIST, default=(['EBAY_US', "USD"], 'USA'))
    condition = SelectMultipleFieldCheckbox(
        "Select conditions", choices=ITEM_CONDITION_LIST)

    submit = SubmitField('Submit')
