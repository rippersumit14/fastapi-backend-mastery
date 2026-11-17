import sqlite3
from typing import Any
from contextlib import contextmanager

from schemas import ShipmentCreate, ShipmentUpdate


class Database:
    def connect_to_db(self):
        # Establish connection to the SQLite database
        self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)
        # Initialize cursor for executing queries
        self.cur = self.conn.cursor()
        print("[SETUP] Connected to database.")

    def create_table(self):
        # Create shipment table if it does not already exist
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS shipment (
                id INTEGER PRIMARY KEY,
                content TEXT,
                weight REAL,
                destination INTEGER,
                status TEXT
            )
        """)
        print("[SETUP] Database table verified.")

    def create(self, shipment: ShipmentCreate) -> int:
        # Retrieve the highest existing ID to auto-increment
        self.cur.execute("SELECT MAX(id) FROM shipment")
        result = self.cur.fetchone()
        
        # Assign ID 1 if the table is empty, else increment by 1
        new_id = result[0] + 1 if result[0] else 1

        # Insert the new shipment record using parameterized queries
        self.cur.execute("""
            INSERT INTO shipment
            VALUES (:id, :content, :weight, :destination, :status)
        """,
            {
                "id": new_id,
                **shipment.model_dump(),
                "status": "placed",
            }
        )
        # Commit the transaction to save changes
        self.conn.commit()
        return new_id

    def get(self, id: int) -> dict[str, Any] | None:
        # Fetch a specific shipment by ID
        self.cur.execute("""
            SELECT * FROM shipment
            WHERE id = ?
        """, (id, ))
        row = self.cur.fetchone()

        if not row:
            return None

        # Fallback safeguard for legacy rows missing the destination column
        if len(row) == 4:
            return {
                "id": row[0],
                "content": row[1],
                "weight": row[2],
                "destination": None,
                "status": row[3],
            }
        
        # Standard mapping for the updated 5-column schema
        return {
            "id": row[0],
            "content": row[1],
            "weight": row[2],
            "destination": row[3],
            "status": row[4],
        }
    
    def update(self, id: int, shipment: ShipmentUpdate) -> dict[str, Any]:
        # Update the status of an existing shipment
        self.cur.execute("""
            UPDATE shipment SET status = :status
            WHERE id = :id
        """, 
            {   
                "id": id,
                **shipment.model_dump()
            }
        )
        self.conn.commit()
        return self.get(id)  # type: ignore
    
    def delete(self, id: int):
        # Remove a shipment record by ID
        self.cur.execute("""
            DELETE FROM shipment
            WHERE id = ?
        """, (id, ))
        self.conn.commit()

    def close(self):
        # Safely close the database connection
        print("[TEARDOWN] Database connection closed.")
        self.conn.close()
        
    def __enter__(self):
        # Initialization logic for the context manager
        print("[SETUP] Entering Context Manager...")
        self.connect_to_db()
        self.create_table()
        return self
     
    def __exit__(self, exc_type, exc_value, traceback):
        # Cleanup logic guaranteed to run upon exiting the block
        print("[TEARDOWN] Exiting Context Manager...")
        self.close()
        

@contextmanager       
def managed_db():
    # Context manager implemented via generator function
    print("[SETUP] Executing @contextmanager setup...")
    db = Database()
    db.connect_to_db()
    db.create_table()
    
    # Pause execution and yield the database instance to the caller
    yield db
    
    # Resume execution and perform resource cleanup
    print("[TEARDOWN] Executing @contextmanager teardown...")
    db.close()


# Execution block for script testing
if __name__ == "__main__":
    print("--- Testing Class Dunder Methods ---")
    with Database() as db:
        print(f"Fetching data for 12701: {db.get(12701)}")

    print("\n--- Testing Decorator Context Manager ---")
    with managed_db() as db:
        print(f"Fetching data for 12702: {db.get(12702)}") 