import socket
from _thread import *
from utils import get_ip_interface

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "0.tcp.ap.ngrok.io"
        print(f"[Network] Local IP detected as: {self.server}")
        self.port = 11116
        self.addr = (self.server, self.port)
        self.connected = False
        self.running = False
        self.messages = []

        self.move = self.connect()
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            msg = self.client.recv(2048).decode()
            print(f"[Network] {msg}")
            self.connected = True
            self.running = True
            start_new_thread(self.listen, ())
        except Exception as e:
            print(f"[Network] Connection error: {e}")
            self.connected = False

    def listen(self):
        while self.running:
            try:
                msg = self.client.recv(2048).decode()
                if msg:
                    msg = msg.strip()
                    print(f"[Server] {msg}")
                    self.messages.append(msg)
                    print(self.messages)
            except ConnectionResetError:
                print("[Network] Server disconnected.")
                break
            except OSError as e:
                print(f"[Network] Listener stopped: {e}")
                break
            except Exception as e:
                print(f"[Network] Listener error: {e}")
        
        self.connected = False
        self.running = False
    
    def send(self, data):
        if not self.connected:
            print("[Network] Cannot send: Not connected.")
            return
        try:
            self.client.sendall(str.encode(data))
        except OSError as e:
            print(f"[Network] Send error: {e}")
            self.close()
        except Exception as e:
            print(f"[Network] Send error: {e}")
    
    def get_message(self):
        if self.messages:
            return self.messages.pop(0)
        return None
    
    def close(self):
        if not self.connected and not self.running:
            return
        
        self.running = False
        self.connected = False

        try:
            self.client.sendall(b"LEAVE")
        except Exception:
            pass

        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        

        try:
            self.client.close()
        except Exception:
            pass

        print("[Network] Connection closed successfully.")