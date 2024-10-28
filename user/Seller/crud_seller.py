from fastapi import APIRouter , status , Security , HTTPException
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from fastapi.responses import JSONResponse 
from user.Seller import schemas_seller
from Authentication.authentication import get_current_user
from database import db_dependency
import model
from typing import List

router = APIRouter(tags=['Seller'])

security = HTTPBearer()

@router.post('/add_shop' , status_code=201)
async def add_shop(req : schemas_seller.add_shop , db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        current_user = get_current_user(token)

        if not current_user:
            raise HTTPException(status_code=404 ,detail="Could not find user")
        else:

            if current_user.get('user_type') != 'seller':
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Could not access this site')

            email = current_user.get('sub')
            user_type = current_user.get('user_type')
            get_user = db.query(model.User).filter(model.User.email ==  email, 
                                                   model.User.user_type == user_type).first()
            
            if not get_user:
                raise HTTPException(status_code=404 ,detail="Could not find user")
            else:
                data = model.Shop(shop_name = req.name , user_id = get_user.id)
                db.add(data)
                db.commit()
                db.refresh(data)

                return JSONResponse(content=data ,status_code=status.HTTP_200_OK)
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f'could not validate user {str(e)}')

@router.post('/add_book' , status_code=status.HTTP_201_CREATED)
async def add_book(req : schemas_seller.add_books , db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):

    try:
        token = credentials.credentials
        current_user = get_current_user(token)

        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="Could find not user")
        else:

            if current_user.get('user_type') !='seller':
                raise HTTPException(status_code=401 , detail='Could not access this site')

            email = current_user.get('sub')
            get_user = db.query(model.User).filter(
                model.User.email == email ,
                model.User.user_type == current_user.get('user_type')).first()
            
            # verifying that this shop does exists
            shop_exists = db.query(model.Shop).filter(model.Shop.shop_name == req.shop_name).first()

            if not shop_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='shop does not exists')
            
            else:
                # verifying that this shop does belong to this specfic user
                shop_owner = db.query(model.Shop).filter(model.Shop.id == shop_exists.id , model.Shop.user_id == get_user.id)

                if not shop_owner:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='You do not own this shop')
                
                else:
                    data = model.Book(book_name = req.book , price = req.price , 
                                stock_quantity = req.stock_quantity , shop_id = shop_exists.id ,
                                user_id = get_user.id)
                    db.add(data)
                    db.commit()
                    db.refresh(data)

                    result = {
                        'shop' : shop_exists.shop_name,
                        'book' : data.book_name,
                        'price' : data.price,
                        'stock_quantity' : data.stock_quantity
                    }
                    return result
                    
    except Exception as exp:
        raise HTTPException(status_code=401 ,detail=f"Could not validate credentials {str(exp)}")
    

@router.get('/my-shops')
async def get_my_shops(db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials

        current_user = get_current_user(token)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Could not found User')
        else:
            if current_user.get('user_type') !='seller':
                raise HTTPException(status_code=401 , detail='Could not access this site')
            else: 
                seller = db.query(model.User).filter(model.User.email == current_user.get('sub')).first()
                get_shops = db.query(model.Shop).filter(model.Shop.user_id == seller.id).all()

                result = []

                for shop in get_shops:

                    books = db.query(model.Book).filter(model.Book.shop_id == shop.id).all()

                    for book in books:

                        result.append(
                            {
                                'Shop name' : shop.shop_name,
                                'book name' : book.book_name,
                                'price' : book.price,
                                'stock quantity' : book.stock_quantity
                            }
                        )

            return result
    except Exception as e :
        raise HTTPException(status_code=401, detail=f"Could not validate credentials {str(e)}")