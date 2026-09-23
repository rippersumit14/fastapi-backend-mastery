#Decorators are some predefined functions that has some logic written over it.
#So these pre-defined functionalitites and their core logic can be implemented in out buisness logic functions.

# 1. The Decorator
def fence(func):
    # 2. The inner wrapper adds the new logic
    def wrapper():
        print("--- Fence Start ---")
        
        # Execute the original function
        func() 
        
        print("--- Fence End ---")
        
    # 3. Return the wrapper function itself (no parentheses!)
    return wrapper 

# 4. Apply the decorator
@fence
def log():
    print("decorated?")

# 5. Call the function normally without passing arguments
log()