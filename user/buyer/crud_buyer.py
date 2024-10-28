from fastapi import APIRouter , Security , HTTPException , status
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from user.buyer import schemas_buyer
from database import db_dependency
from Authentication.authentication import get_current_user
import model
import stripe

router = APIRouter(tags=['Buyer'])
stripe.api_key = "sk_test_51PvyagEjlIT9C6lRUKnmO34qup4uotxzz6XccQxiP1wHPHRRrMk4IUWs0yKTE5klRtt3izPoIqQzzMlHWy9y3GHf00Z3xaHyTV"


security = HTTPBearer()

@router.get('/all-books')
async def get_all_books(db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = get_current_user(token)

        if payload:
            if payload.get('user_type') == 'buyer':
                    
                shops = db.query(model.Shop).all()

                result = []
                for shop in shops:
                    books = db.query(model.Book).filter(model.Book.shop_id == shop.id).all()
                    for book in books:
                        result.append({
                            'shop id' : shop.id,
                            'shop name' : shop.shop_name,
                            'book id' : book.id,
                            'book name' : book.book_name,
                            'book price': book.price,
                            'book quantity' : book.stock_quantity
                        })    

                # books = db.query(model.Book).all()
                # result = []
                # print(books[0].book_name)
                # for book in books:
                    
                #     shop = db.query(model.Shop).filter(model.Shop.id == model.Book.shop_id).first()
                #     result.append(
                #         {   
                #             'shop' : shop.shop_name,
                #             'Book Name' : book.book_name,
                #             'Price' : book.price
                #         }
                #     )
                
                return result
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='You cannot access this API')
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Invalid Token')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f'could not validate credentials {str(e)}')
    
@router.put('/Buy-books')
async def buy(req : schemas_buyer.buy_books , db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = get_current_user(token)

        if payload:
            if payload.get('user_type') == 'buyer':
                
                    is_book = db.query(model.Book).filter(model.Book.id == req.book_id , model.Book.shop_id == req.shop_id).first()

                    if is_book:

                        is_quantity = req.quantity <= is_book.stock_quantity and req.quantity >0 

                        if is_quantity :

                            total_price = req.quantity * is_book.price

                            buyer = db.query(model.User).filter(model.User.email == payload.get('sub')).first()

                            is_cart = db.query(model.Cart).filter(model.Cart.buyer_id == buyer.id).first()

                            if is_cart: # if cart already exists then simply add data into cart

                                add_cartItem = model.CartItem(
                                    quantity = req.quantity , book_id = is_book.id , cart_id = is_cart.id, shop_id = is_book.shop_id
                                )
                                
                                is_cart.total_price += total_price

                                is_book.stock_quantity -= req.quantity

                                db.add(add_cartItem)
                                db.commit()
                                db.refresh(add_cartItem)
                    
                                return add_cartItem
                            
                            else:
                                add_cart = model.Cart(total_price = total_price , buyer_id = buyer.id)
                                db.add(add_cart)
                                db.commit()
                                db.refresh(add_cart)

                                is_cart = db.query(model.Cart).filter(model.Cart.buyer_id == buyer.id).first()


                                add_cartItem = model.CartItem(
                                    quantity = req.quantity , book_id = is_book.id , cart_id = is_cart.id , shop_id = is_book.shop_id
                                )

                                is_book.stock_quantity -= req.quantity

                                db.add(add_cartItem)
                                db.commit()
                                db.refresh(add_cartItem)

                                return {'cart' : add_cart , 
                                        'CartItems' : add_cartItem}

                        else:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Given quantity is more than stock quantity')
                    else:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Shop or book does not exists')
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='You cannot access this API')
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Invalid Token')

    except Exception as exp:
        raise HTTPException(status_code=401 ,detail=f"Could not validate credentials {str(exp)}")
    

@router.post('/Cart')
async def user_cart( db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = get_current_user(token)

        if payload:
            if payload.get('user_type') == 'buyer':
                buyer = db.query(model.User).filter(model.User.email == payload.get('sub')).first()
                # 1 user can have 1 cart at a time

                is_cart = db.query(model.Cart).filter(model.Cart.buyer_id == buyer.id).first()

                if is_cart:
                    # need to return the name, price , quantity
                    cartItem = db.query(model.CartItem).filter(model.CartItem.cart_id == is_cart.id).all()

                    result = []
                    
                    result.append({'Cart total price' : is_cart.total_price})

                    for product in cartItem:
                        result.append(
                            {
                                'book' : db.query(model.Book).filter(model.Book.id == product.book_id).first().book_name,
                                'quantity' : product.quantity,
                            }
                        )
                    

                    return result
                else:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='No product in cart')
                
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='You cannot access this API')
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Invalid Token')

    except Exception as exp:
        raise HTTPException(status_code=401 ,detail=f"Could not validate credentials {str(exp)}")


@router.post("/process-payment/")
async def process_payment(db : db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
    try:

        token = credentials.credentials
        payload = get_current_user(token)

        if payload:

            buyer = db.query(model.User).filter(model.User.email == payload.get('sub')).first()
            cart = db.query(model.Cart).filter(model.Cart.buyer_id == buyer.id).first()

            if cart:
                ## making a payment intent
                print("Stripe balance : \n",stripe.Balance.retrieve())

                intent = stripe.PaymentIntent.create(
                    # amount= int(cart.total_price * 100), # as stripe accept the payment in cents
                    # currency= 'usd',
                    # metadata={'cart_id' : cart.id , 'user_email' : buyer.email},
                    amount=int(cart.total_price * 100),  # Stripe accepts the payment amount in cents
                    currency='usd',
                    automatic_payment_methods={"enabled": True},
                    metadata={'cart_id': cart.id, 'user_email': buyer.email},
                )

                ## creating a payment record
                payment = model.Payment(
                    amount=cart.total_price,
                    payment_method='stripe',
                    payment_status='pending',
                    user_id=buyer.id
                )
                db.add(payment)

                ## now deleting the cartItem and the entire Cart

                cart_items = db.query(model.CartItem).filter(model.CartItem.cart_id == cart.id).all()
                for items in cart_items:
                    db.delete(items)
                db.delete(cart)

                db.commit()

                return {"payment id" : intent.id  , "clientSecret": intent.client_secret}

            else:
                raise HTTPException(status_code=404 , detail='No Cart to be founded')
        
        else:
            raise HTTPException(status_code=401 , detail='User Unathorized')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f'Could not validate Credentials {str(e)}')

@router.post("/confirm-payment/")
async def confirm_payment(payment_intent_id: str, db: db_dependency, credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        # Step 1: Authenticate the user
        token = credentials.credentials
        payload = get_current_user(token)
        
        if not payload or payload.get('user_type') != 'buyer':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized access')

        # Step 2: Retrieve the PaymentIntent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        print("Payment Intent Status: ", intent.status)

        # Step 3: Check if the payment was successful
        if intent.status == 'succeeded':
            # Step 4: Update the Payment record
            user = db.query(model.User).filter(model.User.email == payload.get('sub')).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

            payment = db.query(model.Payment).filter(model.Payment.user_id == user.id).order_by(model.Payment.id.desc()).first()
            if payment:
                payment.payment_status = 'completed'
                db.add(payment)
                db.commit()
            
            return {"status": "Payment successful"}
        else:
            print("Payment Intent Details: ", intent)
            # If payment failed, you might want to handle this case (e.g., retry, notify user, etc.)
            return {"status": "Payment failed", "details": intent.last_payment_error}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.delete('/cart')
# async def delete_cart(db:db_dependency , credentials : HTTPAuthorizationCredentials = Security(security)):
#     try:
#         token = credentials.credentials
#         payload = get_current_user(token)

#         if payload:
#             if payload.get('user_type') == 'buyer':


    
#     except Exception as exp:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f'could not validate credentials {str(exp)}')