# Socket Transaction Server

This project implements a transactional key-value store with ACID properties using raw socket connections in Python. This low-level approach gives more control over the server's behavior but may be more complex than using a high-level framework.

## Concurrency

This server uses a combination of threading and lock-based synchronization to manage access to shared resources across multiple clients. As such, it is able to handle concurrent requests in a safe way, given certain conditions. It also includes support for transactions, with operations including START, COMMIT, ROLLBACK, PUT, DELETE, GET, and VIEW.

### Safety Across Operations

#### TLDR;

The server employs key-level locking to handle multiple concurrent transactions on the same keys, and deadlock prevention is achieved by always acquiring locks in a sorted order.

#### Safety mechanisms:

1. Starting a Transaction (START): This operation is safe, as it involves creating a new transaction and adding it to the transactions dictionary using a unique transaction ID. It's safe because Python's built-in data types, like dictionaries, are thread-safe for single operations.

2. Committing a Transaction (COMMIT): This operation removes a transaction from the transactions dictionary and applies its changes to the main data store. It acquires a lock for each key involved in the transaction before updating the main data store and saving it to a file. This lock-based synchronization ensures that data inconsistencies do not arise due to concurrent commits that affect the same keys.

3. Rolling Back a Transaction (ROLLBACK): This operation is also safe as it involves removing a transaction from the transactions dictionary, which is a single, atomic operation. Locks for each key involved in the transaction are acquired and then released after the operation, ensuring no other operations can interfere during the rollback.

4. Adding/Updating a Key-Value Pair (PUT): This operation is thread-safe because it operates on the transaction's isolated copy of the data. When adding or updating a key-value pair, a lock is acquired for the key to prevent race conditions.

5. Deleting a Key-Value Pair (DELETE): Similar to the PUT operation, this operation is thread-safe within a transaction and uses a key-based lock to prevent race conditions when operating on the shared data store.

6. Retrieving a Key-Value Pair (GET, VIEW): These operations are safe because they only involve reading data from the transaction's data or from the main data store. In the case of retrieving from the main data store, a lock is used to ensure a consistent view of the data is provided to the client.

## Maintaining ACID with Transaction ID

Transaction ID was implemented to track and manage transactions. By incorporating Transaction ID we gain the following features:

1. Isolation: In a multi-client environment, each client might be performing multiple operations as part of separate transactions. The transaction ID is what allows the server to keep track of which operations belong to which transaction. This is necessary to ensure that each transaction is isolated from others.

2. Atomicity: The transaction ID allows the server to group several operations together as a single transaction. This is necessary to ensure atomicity, i.e., either all operations in a transaction are performed, or none of them are.

3. Commit or Rollback: The transaction ID is used to specify which transaction should be committed or rolled back. When a client sends a 'COMMIT' or 'ROLLBACK' command, the server uses the transaction ID provided in the command to find the corresponding transaction.

4. Consistency: By using transaction IDs, the server can ensure that only consistent sets of changes (those belonging to a fully committed transaction) are applied to the main data store.

In summary, without a transaction ID, the server would have no way to determine which operations belong to which transaction, making it impossible to provide the ACID guarantees (Atomicity, Consistency, Isolation, Durability) that transactions are supposed to provide.

## How to use

1. Make sure you have Python 3.6+ installed.
2. Run the server using `python main.py`.
3. The server will start and listen for connections on `localhost:12345`.

## Docker

This server can be run in a Docker container. To do so, follow these steps:

1. Ensure you have Docker installed.
2. Build the Docker image with `docker build -t socket-server .`
3. Run the Docker container with `docker run -d -p 12345:12345 socket-server`

The server should now be accessible at `localhost:12345`.

## Commands

Commands are sent as JSON objects over the socket connection. Here are the available commands:

- `START`: Starts a new transaction.
- `COMMIT`: Commits a transaction.
- `ROLLBACK`: Rolls back a transaction.
- `PUT`: Puts a key-value pair into the data store.
- `DELETE`: Deletes a key-value pair from the data store.
- `GET`: Retrieves a value from the data store.
- `VIEW`: Retrieves the entire data store.

See the Python `socket` module documentation for more information on using sockets.

## Interacting with the Server using Jupyter Notebooks

You can find test cases in Jupyter notebooks in the `test_cases` folder. To run these test cases:

1. Ensure you have Jupyter notebook installed. You can install it with `pip install jupyter`.
2. Navigate to the `test_cases` folder and open the Jupyter notebook file.
3. Run the notebook cells to interact with the server.

## Deployment to Google Kubernetes Engine (GKE)

You can deploy this server to GKE by following these steps:

1. Build the Docker image for the Socket server: `docker build -t gcr.io/<PROJECT_ID>/socket-server .`
2. Push the Docker image to Google Container Registry: `docker push gcr.io/<PROJECT_ID>/socket-server`
3. Create a deployment in GKE using the image: `kubectl create deployment socket-server --image=gcr.io/<PROJECT_ID>/socket-server`
4. Expose the deployment to the internet: `kubectl expose deployment socket-server --type=LoadBalancer --port 80 --target-port 12345`
5. Replace <PROJECT_ID> with your Google Cloud project ID. You'll also need the gcloud, docker, and kubectl command-line tools installed and configured.