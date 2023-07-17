import socket
import threading
import json
import uuid
from collections import defaultdict

class TransactionServer:
    def __init__(self, host='localhost', port=12345):
        """Initialize the server with a host and port to listen to."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.data = self.load_data()  # Main storage of key-value pairs (committed data)
        self.transactions = {}  # Uncommitted transactions
        self.key_locks = defaultdict(threading.Lock)  # Lock for each key for synchronization

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
        """
        cmd = command.get('cmd')
        key = command.get('key')
        value = command.get('value')
        id = command.get('id')

        if cmd == 'START':
            # Generate a new transaction ID
            transaction_id = str(uuid.uuid4())
            # Starts a new transaction
            self.transactions[transaction_id] = {}
            return {'status': 'Ok', 'mesg': 'Transaction started', 'transaction_id': transaction_id}

        elif cmd in ['PUT', 'DELETE']:
            # Add or delete a key-value pair
            if not id in self.transactions:
                return {'status': 'Error', 'mesg': 'Transaction not found'}

            # Always acquire locks in a sorted order to prevent deadlocks
            keys = sorted(list(self.transactions[id].keys()) + [key])
            locks = [self.key_locks[k] for k in keys]

            for lock in locks:
                lock.acquire()

            if cmd == 'PUT':
                self.transactions[id][key] = value
                result = {'status': 'Ok', 'mesg': 'Key-value pair added/updated'}
            else:  # cmd == 'DELETE'
                if key in self.transactions[id]:
                    del self.transactions[id][key]
                result = {'status': 'Ok', 'mesg': 'Key-value pair deleted'}

            # Release locks
            for lock in reversed(locks):
                lock.release()

            return result

        elif cmd == 'COMMIT':
            # Commit a transaction
            if not id in self.transactions:
                return {'status': 'Error', 'mesg': 'Transaction not found'}

            # Always acquire locks in a sorted order to prevent deadlocks
            keys = sorted(self.transactions[id].keys())
            locks = [self.key_locks[k] for k in keys]

            for lock in locks:
                lock.acquire()

            self.data.update(self.transactions.pop(id, {}))
            self.save_data()  # save committed changes to a file

            # Release locks
            for lock in reversed(locks):
                lock.release()

            return {'status': 'Ok', 'mesg': 'Transaction committed'}

        elif cmd == 'ROLLBACK':
            # Roll back a transaction
            if id in self.transactions:
                keys = self.transactions[id].keys()
                locks = [self.key_locks[k] for k in keys]

                for lock in locks:
                    lock.acquire()

                self.transactions.pop(id, None)

                # Release locks
                for lock in reversed(locks):
                    lock.release()

                return {'status': 'Ok', 'mesg': 'Transaction rolled back'}
            else:
                return {'status': 'Error', 'mesg': 'Transaction not found'}

        elif cmd == 'GET':
            # Get the value for a key or retrieve the entire database
            if key:
                lock = self.key_locks[key]
                lock.acquire()
                result = {'status': 'Ok', 'result': self.data.get(key)}
                lock.release()
                return result
            else:
                return {'status': 'Error', 'mesg': 'Key not provided'}

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
