from pydantic import BaseModel

class add_shop(BaseModel):
    name : str

    class Config:
        from_attributes = True

class add_books(BaseModel):
    shop_name : str
    book : str
    price : float
    stock_quantity : int

    class Config:
        from_attributes = True

class get_shops(BaseModel):
    shop_name : str
    # books : add_books

    class Config:
        from_attributes = True