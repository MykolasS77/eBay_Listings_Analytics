from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from .country_codes import COUNTRY_CODES


class SelectMultipleFieldCheckbox(SelectMultipleField):

    """
    Turns multiple options field to checkbox select field. It was needed to select several options at once.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


"""
CURRENCY_LIST holds currency codes which are used for conversion.
"""

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

"""
The list inside MARKET_LIST consists of country code and the default currency, which are needed when making calls to eBay API. 
"""

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


class SearchForm(FlaskForm):

    """
    The search form.
    """

    search_parameter = StringField('Search Parameter', validators=[
                                   DataRequired(), Length(max=100)])
    delivery_destination = SelectField(
        'Select Delivery Country', choices=COUNTRY_CODES, validators=[DataRequired()])
    free_shipping = BooleanField(
        'Free Shipping:', validators=[Optional()])
    limit = IntegerField("Items Limit", validators=[
                         Optional(), NumberRange(min=0, max=200)])
    sort_by = SelectField('Sort By', choices=[(
        None, "-----"), ("price", "Price: lowest to highest"), ("-price", "Price: highest to lowest")], validators=[Optional()])
    price_filter_min = IntegerField("Minimum Price", validators=[Optional()])
    price_filter_max = IntegerField("Maximum Price", validators=[Optional()])
    currency = SelectField('Convert To Currency',
                           choices=CURRENCY_LIST, validators=[Optional()])
    market = SelectMultipleFieldCheckbox(
        'Select Markets:', choices=MARKET_LIST, default=(['EBAY_US', "USD"], 'USA'))
    condition = SelectMultipleFieldCheckbox(
        "Select Conditions:", choices=[("NEW", "New"), ("USED", "Used")], validators=[Optional()])

    submit = SubmitField('Submit')
