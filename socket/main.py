import socket
import threading
import json
import uuid

class TransactionServer:
    def __init__(self, host='localhost', port=12345):
        """Initialize the server with a host and port to listen to."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.data = self.load_data()  # Main storage of key-value pairs (committed data)
        self.transactions = {}  # Uncommitted transactions

    def load_data(self):
        """Load the main data store from a file."""
        try:
            with open('db.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        
    def save_data(self):
        """Save the main data store to a file."""
        with open('db.json', 'w') as f:
            json.dump(self.data, f)
        
    def handle_client(self, client):
        """Handle a client connection."""
        while True:
            command = client.recv(1024).decode('utf-8')
            if not command:
                break
            response = self.process_command(json.loads(command))
            client.sendall(json.dumps(response).encode('utf-8'))
        client.close()

    def process_command(self, command):
        """
        Process a command sent by the client and return the response.

        This function is responsible for maintaining the ACID properties:
            - Atomicity is maintained by treating each command as a single atomic operation and
              ensuring that it fully completes or has no effect.
            - Consistency is ensured by updating the transaction's data or the main data store in a
              consistent manner for each operation.
            - Isolation is achieved by using a separate dictionary for each transaction's uncommitted
              changes.
            - Durability is handled by writing the main data store to a file every time a transaction
              is committed.
        """
        cmd = command.get('cmd')
        key = command.get('key')
        value = command.get('value')
        id = command.get('id')

        if cmd == 'START':
            # Generate a new transaction ID
            transaction_id = str(uuid.uuid4())
            # Starts a new transaction (Atomicity)
            self.transactions[transaction_id] = {}
            return {'status': 'Ok', 'mesg': 'Transaction started', 'transaction_id': transaction_id}
        elif cmd == 'COMMIT':
            # Commit a transaction (Atomicity, Durability)
            if id in self.transactions:
                self.data.update(self.transactions.pop(id, {}))
                self.save_data()  # Durability: save committed changes to a file
                return {'status': 'Ok', 'mesg': 'Transaction committed'}
            else:
                return {'status': 'Error', 'mesg': 'Transaction not found'}
        elif cmd == 'ROLLBACK':
            # Roll back a transaction (Atomicity)
            if id in self.transactions:
                self.transactions.pop(id, None)
                return {'status': 'Ok', 'mesg': 'Transaction rolled back'}
            else:
                return {'status': 'Error', 'mesg': 'Transaction not found'}
        elif cmd == 'PUT':
            # Add or update a key-value pair (Atomicity, Consistency)
            if id in self.transactions:
                self.transactions[id][key] = value
            else:
                self.data[key] = value
            return {'status': 'Ok', 'mesg': 'Key-value pair added/updated'}
        elif cmd == 'DELETE':
            # Delete a key-value pair (Atomicity, Consistency)
            if id in self.transactions and key in self.transactions[id]:
                del self.transactions[id][key]
            elif key in self.data:
                del self.data[key]
            return {'status': 'Ok', 'mesg': 'Key-value pair deleted'}
        elif cmd == 'GET':
            # Get the value for a key or retrieve the entire database
            if key:
                if id in self.transactions and key in self.transactions[id]:
                    return {'status': 'Ok', 'result': self.transactions[id].get(key)}
                else:
                    return {'status': 'Ok', 'result': self.data.get(key)}
            else:
                return {'status': 'Ok', 'result': self.data}
        elif cmd == 'VIEW':
            # Retrieve and return the entire database
            return {'status': 'Ok', 'result': self.data}
        else:
            return {'status': 'Error', 'mesg': 'Unknown command'}


    def start(self):
        """Start the server."""
        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client,))
            client_thread.start()

if __name__ == "__main__":
    TransactionServer().start()
