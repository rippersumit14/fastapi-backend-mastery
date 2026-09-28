from pydantic import BaseModel, Field
from random import randint

def random_destination():
    return randint(11000, 11999)




class Shipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(description="Weight of the shipment is in kilograms", lt=25, ge=1)
    destination: int | None = Field(default_factory=random_destination)
    
#This is the basemodel schema 
#The data validation library 


    