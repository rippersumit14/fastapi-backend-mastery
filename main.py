from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference
from fastapi.responses import RedirectResponse



# Assuming schemas.py is in root and database.py is in app/ based on previous fixes
from schemas import ShipmentCreate, ShipmentUpdate, ShipmentRead
from app.database import shipments, save

# Initialize FastAPI application with a custom title
app = FastAPI(title="Shipment Management API")


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int):
    """
    Retrieve a specific shipment by its unique ID.
    """
    # Guard clause: Check if shipment exists before accessing
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} doesn't exist"
        )
        
    return shipments[id]


@app.post("/shipment", status_code=status.HTTP_201_CREATED)
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:
    """
    Create a new shipment, assign an auto-incremented ID, and persist to disk.
    """
    # Generate a new unique ID safely (prevents crash if the database is empty)
    new_id = max(shipments.keys()) + 1 if shipments else 1
    
    # Hydrate the dictionary with validated data and default backend fields
    shipments[new_id] = {
        **shipment.model_dump(),
        "id": str(new_id), # Ensuring ID type consistency if your JSON expects strings
        "status": "placed",
    }
    
    # Persist in-memory dictionary changes to the JSON file
    save()
    
    return {"id": new_id}


@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int, body: ShipmentUpdate):
    """
    Partially update an existing shipment (e.g., updating its tracking status).
    """
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} doesn't exist"
        )
        
    # Convert validated Pydantic model to a Python dict. 
    # exclude_unset=True ensures we only update fields the client explicitly provided.
    update_data = body.model_dump(exclude_unset=True)
    shipments[id].update(update_data)
    
    save()
    
    return shipments[id]
    

@app.delete("/shipment")
def delete_shipment(id: int) -> dict[str, str]:
    """
    Remove a shipment entirely from the datastore by its ID.
    """
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} doesn't exist"
        )
        
    # Safely pop the record from the dictionary
    shipments.pop(id)
    
    # Persist the deletion to the JSON file so it doesn't reappear on server restart
    save()

    return {"detail": f"Shipment with id #{id} is deleted!"}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    """
    Serve the modern Scalar API Documentation interface.
    (include_in_schema=False prevents this endpoint from documenting itself)
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API Docs - Shipment Management",
    )
    
    
@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/scalar")

