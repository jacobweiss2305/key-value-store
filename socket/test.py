import socket
import json
import time

def send_command(s, cmd, id=None, key=None, value=None):
    """Send a command to the server and print the response."""
    command = {'cmd': cmd}
    if id is not None:
        command['id'] = id
    if key is not None:
        command['key'] = key
    if value is not None:
        command['value'] = value
    s.sendall(json.dumps(command).encode('utf-8'))
    response = json.loads(s.recv(1024).decode('utf-8'))
    print(f"Response: {response}")

def test_client():
    """Test the functionality of the server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 12345))
        
        print("Starting transaction 1...")
        send_command(s, 'START', id=1)
        
        print("Adding key1=value1 in transaction 1...")
        send_command(s, 'PUT', id=1, key='key1', value='value1')

        print("Attempting to retrieve key1 outside of transaction 1 (should not be visible)...")
        send_command(s, 'GET', key='key1')

        print("Committing transaction 1...")
        send_command(s, 'COMMIT', id=1)

        print("Attempting to retrieve key1 after transaction 1 committed (should be visible)...")
        send_command(s, 'GET', key='key1')

        print("Deleting key1...")
        send_command(s, 'DEL', key='key1')

        print("Attempting to retrieve key1 after deletion (should not be visible)...")
        send_command(s, 'GET', key='key1')

if __name__ == "__main__":
    test_client()
