from fastapi import FastAPI
import models
from database import Base,engine
from routers import product,category,supplier,customer,user,inventory,sale,sale_item,payment,receipt

Base.metadata.create_all(bind=engine) 

app=FastAPI(title="POS API",version="1")
app.include_router(product.router)
app.include_router(category.router)
app.include_router(supplier.router)
app.include_router(customer.router)
app.include_router(user.router)
app.include_router(inventory.router)
app.include_router(sale.router)
app.include_router(sale_item.router)
app.include_router(payment.router)
app.include_router(receipt.router)