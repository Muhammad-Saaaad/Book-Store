from fastapi import FastAPI

from user.Seller import crud_seller
from user.buyer import crud_buyer
from Authentication import authentication
from database import base , engine

app = FastAPI()

# study on middleware like cors

base.metadata.create_all(engine)

app.include_router(authentication.router)
app.include_router(crud_seller.router)
app.include_router(crud_buyer.router)