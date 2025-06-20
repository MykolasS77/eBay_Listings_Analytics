from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


"""
   SavedData table is used to put recieved json format files from the eBay API. 
   It has a one to many relationship with GeneralQueryData, which holds median, average, min, max price for items recieved from each region selected in search.
   GeneralQueryData has one to many relationship with SingleItem, which holds information about each recieved product. 
"""


class SavedData(db.Model):
    __tablename__ = "saved_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    search_parameter: Mapped[str] = mapped_column(unique=False)
    market_list: Mapped[str] = mapped_column(unique=False)
    data: Mapped[str] = mapped_column()

    general_query_data: Mapped[List["GeneralQueryData"]
                               ] = relationship(back_populates="saved_data")


class GeneralQueryData(db.Model):
    __tablename__ = "general_query_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column()
    average_price: Mapped[int] = mapped_column()
    min_price: Mapped[int] = mapped_column()
    max_price: Mapped[int] = mapped_column()
    median_price: Mapped[int] = mapped_column()
    market: Mapped[str] = mapped_column()

    parent_id: Mapped[int] = mapped_column(ForeignKey("saved_data.id"))

    items: Mapped[List["SingleItem"]] = relationship(
        back_populates="general_query_data")
    saved_data: Mapped["SavedData"] = relationship(
        back_populates="general_query_data")


class SingleItem(db.Model):
    __tablename__ = "single_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    shipping_price: Mapped[int] = mapped_column()
    total_price: Mapped[int] = mapped_column()
    seller: Mapped[str] = mapped_column()
    condition: Mapped[str] = mapped_column()
    link_to_product: Mapped[str] = mapped_column()
    image_href: Mapped[str] = mapped_column()
    market: Mapped[str] = mapped_column()

    parent_id: Mapped[int] = mapped_column(ForeignKey("general_query_data.id"))
    general_query_data: Mapped["GeneralQueryData"] = relationship(
        back_populates="items")
