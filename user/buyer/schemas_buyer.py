from pydantic import BaseModel


class get_books_for_buyer(BaseModel):
    id : int
    name : str
    price : float
    shop : str

    class Config:
        from_attributes = True

class buy_books(BaseModel):
    shop_id : int
    book_id : int
    quantity : int

class sub_cart(BaseModel):
    book_id : int