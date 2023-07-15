# In-Memory Key/Value Store with Transactions

This server is an in-memory key/value store that supports transactions. The use case for this server is as a high-performance cache. All commands and server responses are encoded as UTF-8 strings.

## Setup

This server requires Python 3.6 or higher. You can check your Python version by running:

```bash
python --version
```

## Running the Server

To start the server, navigate to the directory containing the server script and run the following command:

```bash
python main.py
```

The server will start and listen for connections on localhost port 9999.

## Running the Tests

This repository includes a test script (test.py) that validates the functionality of the server.

Before running the tests, make sure the server is running. Then, in a separate terminal window, navigate to the directory containing test.py and run:

```bash
python test.py
```

This will run the tests and print the results to the terminal.

## Assumptions and Decisions

- The server supports multiple transactions at the same time using thread-local storage.

- If a transaction is not committed or rolled back, its changes will not be visible to other transactions.

- We use Python's built-in socketserver module for the server and socket module for the test client. These modules provide a simple and efficient way to create a socket server and client in Python.

- JSON is used for server responses because it's a widely used data interchange format that can easily be parsed and generated in many programming languages, including Python.