from sqlalchemy import create_engine
from sqlmodel import SQLModel


engine = create_engine(
    url="sqlite:///sqlite.db", #Make the connection with the database 
    echo=True, #Get the sql statements executed on our database and printed on the terminal
    connect_args = {"check_same_thread": False},
    
)

from .models import Shipment
SQLModel.metadata.create_all(bind=engine) #Table names, columns and it's types.

