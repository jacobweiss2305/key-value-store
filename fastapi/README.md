# FastAPI Transaction Server

This project uses FastAPI to implement a transactional key-value store with ACID properties. FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

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