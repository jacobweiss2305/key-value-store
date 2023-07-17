# FastAPI Transaction Server

This project uses FastAPI to implement a transactional key-value store with ACID properties. FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

## Concurrency
This server uses a combination of threading and lock-based synchronization to manage access to shared resources across multiple clients. As such, it is able to handle concurrent requests in a safe way, given certain conditions. It also includes support for transactions, with operations including START, COMMIT, ROLLBACK, PUT, DELETE, GET, and VIEW.

### Safety Across Operations

#### TLDR;

The FastAPI Server ensures transaction safety by implementing key-level locks, restricting the modification of a key to one transaction at a time. It also limits to one active transaction at a time to avoid conflicts. These measures protect against data inconsistencies in a concurrent environment. Please note, read operations are not isolated, and they can read uncommitted data.

#### Safety mechanisms:

1. START Transaction: In the provided code, only one transaction can be active at a time. When a client requests a new transaction, the system first checks if there is already an active transaction. If one exists, it denies the request and throws an HTTPException with status 409 (Conflict), ensuring safety against conflicting transactions.

2. COMMIT Transaction: When a transaction is committed, the changes are written to the database file, the keys used in the transaction are released, and the transaction is removed from the active transactions dictionary. The operation is performed inside a critical section protected by a lock, which guarantees the safety of the operation.

3. ROLLBACK Transaction: Similar to the commit operation, the rollback operation also removes the transaction from the active transactions dictionary and releases the keys that were locked by the transaction. It's also performed within a critical section protected by a lock, making it safe against concurrent operations.

4. ADD_OR_UPDATE (PUT) Operation: The add_or_update operation checks if the key it's trying to write to is currently in use by another transaction. If it is, the operation is denied to avoid conflicts. This operation is performed within a critical section protected by a lock, making it thread-safe.

5. DELETE Operation: Similar to the add_or_update operation, the delete operation also checks if the key it's trying to delete is currently being used by another transaction. If it is, the operation is denied to prevent conflicts. The operation is performed within a critical section protected by a lock, ensuring thread safety.

6. GET Operation: The get operation is safe as it is only reading data. However, note that it is not isolated; it reads the data directly from the database, so it can read data that is part of uncommitted transactions.


## Maintaining ACID with Transaction ID

Transaction ID was implemented to track and manage transactions. By incorporating Transaction ID we gain the following features:

1. Isolation: In a multi-client environment, each client might be performing multiple operations as part of separate transactions. The transaction ID is what allows the server to keep track of which operations belong to which transaction. This is necessary to ensure that each transaction is isolated from others.

2. Atomicity: The transaction ID allows the server to group several operations together as a single transaction. This is necessary to ensure atomicity, i.e., either all operations in a transaction are performed, or none of them are.

3. Commit or Rollback: The transaction ID is used to specify which transaction should be committed or rolled back. When a client sends a 'COMMIT' or 'ROLLBACK' command, the server uses the transaction ID provided in the command to find the corresponding transaction.

4. Consistency: By using transaction IDs, the server can ensure that only consistent sets of changes (those belonging to a fully committed transaction) are applied to the main data store.

In summary, without a transaction ID, the server would have no way to determine which operations belong to which transaction, making it impossible to provide the ACID guarantees (Atomicity, Consistency, Isolation, Durability) that transactions are supposed to provide.

## Running the Server Locally

1. Make sure you have Python 3.6+ and FastAPI installed. You can install FastAPI with `pip install -r requirements.txt`.
2. Run the server using `uvicorn main:app --reload`.
3. The server will start on `http://localhost:8000`.

## Docker

This server can be run in a Docker container. To do so, follow these steps:

1. Ensure you have Docker installed.
2. Build the Docker image with `docker build -t fastapi-server .`
3. Run the Docker container with `docker run -p 8000:8000 fastapi-server`

The server should now be accessible at `http://localhost:8000`.

## Endpoints

- `POST /start`: Starts a new transaction.
- `POST /commit`: Commits a transaction.
- `POST /rollback`: Rolls back a transaction.
- `POST /put`: Puts a key-value pair into the data store.
- `DELETE /delete`: Deletes a key-value pair from the data store.
- `GET /get`: Retrieves a value from the data store.
- `GET /view`: Retrieves the entire data store.

## Interacting with the Server using Jupyter Notebooks

You can find test cases in Jupyter notebooks in the `test_cases` folder. To run these test cases:

1. Ensure you have Jupyter notebook installed. You can install it with `pip install jupyter`.
2. Navigate to the `test_cases` folder and open the Jupyter notebook file.
3. Run the notebook cells to interact with the server.

## Deployment to Google Kubernetes Engine (GKE)

You can deploy this server to GKE by following these steps:

1. Build the Docker image for the FastAPI server: `docker build -t gcr.io/<PROJECT_ID>/fastapi-server .`
2. Push the Docker image to Google Container Registry: `docker push gcr.io/<PROJECT_ID>/fastapi-server`
3. Create a deployment in GKE using the image: `kubectl create deployment fastapi-server --image=gcr.io/<PROJECT_ID>/fastapi-server`
4. Expose the deployment to the internet: `kubectl expose deployment fastapi-server --type=LoadBalancer --port 80 --target-port 8000`
5. Replace <PROJECT_ID> with your Google Cloud project ID. You'll also need the gcloud, docker, and kubectl command-line tools installed and configured.
