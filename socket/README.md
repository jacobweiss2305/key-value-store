# Socket Transaction Server

This project implements a transactional key-value store with ACID properties using raw socket connections in Python. This low-level approach gives more control over the server's behavior but may be more complex than using a high-level framework.

## Running the Server Locally

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