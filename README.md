# In-memory key-value datastore using ACID principles:

## Comparison between FastAPI and Socket

1. FastAPI
    - FastAPI is based on HTTP protocol, which is a stateless protocol primarily designed for the web.
    - FastAPI, being based on HTTP, is stateless by nature - each request is processed independently and there's no built-in notion of ongoing sessions.
    - FastAPI, especially when coupled with an ASGI server like Uvicorn or Hypercorn, can handle thousands of requests concurrently due to its asynchronous nature.
    - FastAPI comes with a lot of "batteries included" - automatic request and response handling, data validation and serialization, automatic API documentation, dependency injection, etc.
    - FastAPI, being an HTTP server, can easily be used with any HTTP client - which includes browsers, command-line tools like curl, and countless libraries in all programming languages.

2. Socket
    - Socket servers typically use the TCP or UDP protocols, which allow for lower-level networking communication.
    - Socket servers, on the other hand, typically maintain a connection for a period of time, allowing state to be preserved across multiple requests. This stateful nature of socket servers allows them to maintain ongoing transactions, which can be very useful in some scenarios.
    - A simple implementation of a socket server might only handle one connection at a time per thread. More advanced or customized concurrency models are possible with socket servers, but they require more manual implementation.
    - Socket servers are more barebones - they give you a lot of control, but you have to implement many things yourself.
    - Socket servers require a compatible socket client, which can be a bit more involved to set up

To summarize: FastAPI is great when you're building a web API and you want to get a lot done quickly and correctly, while a socket server might be more suitable for more customized use-cases, lower-level networking needs, or when you need to maintain stateful connections.

## Applying ACID principles:

1. Atomicity:

    - Each command received from the client is treated as a single atomic operation. The server ensures that each command is fully completed or has no effect. For example, when a transaction starts or rolls back, it is treated as an atomic operation.

2. Consistency:

    - The server ensures that the data is updated or modified in a consistent manner for each operation. The key-value pairs are stored either in the transaction's data (uncommitted changes) or in the main data store (committed data). When a PUT or DELETE command is received, the server updates the appropriate dictionary (transaction's data or main data store) based on the presence of a transaction ID. When a GET or VIEW command is received, the server retrieves the value from the transaction's data or the main data store based on the presence of a transaction ID.

3. Isolation:

    - Each transaction's uncommitted changes are stored in a separate dictionary. When a PUT or DELETE command is received within a transaction, the changes are applied to the transaction's data dictionary, ensuring isolation from other transactions. The server maintains the isolation between transactions by using separate dictionaries for each transaction's changes.

4. Durability:

    - The main data store, which contains the committed data, is saved to a file every time a transaction is committed. The save_data() method writes the main data store to the db.json file, ensuring that the committed changes persist even if the server is restarted.