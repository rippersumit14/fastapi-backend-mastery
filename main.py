from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from schemas import ShipmentCreate, ShipmentUpdate, ShipmentRead
from app.database import Database

# Initialize FastAPI application with a custom title
app = FastAPI(title="Shipment Management API")

# Initialize and setup the database connection
db = Database()
db.connect_to_db()
db.create_table()


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int):
    """
    Retrieve a specific shipment by its unique ID.
    """
    shipment = db.get(id)
    
    # Guard clause: Check if shipment exists before returning
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} doesn't exist"
        )
        
    return shipment


@app.post("/shipment", status_code=status.HTTP_201_CREATED)
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:
    """
    Create a new shipment, assign an auto-incremented ID, and persist to disk.
    """
    new_id = db.create(shipment) 
    return {"id": new_id}


@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int, body: ShipmentUpdate):
    """
    Partially update an existing shipment (e.g., updating its tracking status).
    """
    # Guard clause: Verify the shipment exists in the database
    if db.get(id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} doesn't exist"
        )
        
    # Update the data in SQLite and return the updated record
    updated_shipment = db.update(id, body)
    return updated_shipment


@app.delete("/shipment")
def delete_shipment(id: int) -> dict[str, str]:
    """
    Remove a shipment entirely from the datastore by its ID.
    """
    # Guard clause: Verify the shipment exists before trying to delete
    if db.get(id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} doesn't exist"
        )
        
    # Delete the record from SQLite
    db.delete(id)

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
    """
    Redirect the root URL to the API documentation.
    """
    return RedirectResponse(url="/scalar")