import socket
import sys
from _thread import *
from utils import get_ip_interface

# server = get_ip_interface()
server = "0.0.0.0" 
port = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)
    s.close()
    sys.exit(1)

s.listen(10)
print("Waiting for connection, server started.")

rooms = {} # {code: [host_conn, client_conn]}
lock = False

def broadcast(room_code, message, sender=None):
    players = rooms.get(room_code, [])
    for p in players[:2]:
        if p and p != sender:
            try:
                p.send(str.encode(message))
            except Exception:
                pass

def threaded_client(conn, addr):
    print("New connection from: ", addr)
    conn.send(str.encode("CONNECTED"))

    
    room_code = None
    player_role = None # 1 = host / 2 = client

    try:
        while True:
            data: str = conn.recv(2048).decode()
            if not data:
                print("Disconnected")
                break

            print(f"[{addr}] {data}")
            
            if data.startswith("HOST:"):
                room_code = data.split(":")[1]
                rooms[room_code] = [conn, None, False, False]
                player_role = 1
                print(f"[ROOM {room_code}] Host created")

            elif data.startswith("JOIN:"):
                room_code = data.split(":")[1]
                if room_code in rooms and rooms[room_code][1] is None:
                    rooms[room_code][1] = conn
                    player_role = 2
                    host_conn = rooms[room_code][0]
                    try:
                        host_conn.send(str.encode("JOINED"))
                    except:
                        pass
                    print(f"[ROOM {room_code}] Player 2 joined")
                else:
                    conn.sendall(str.encode("Invalid code / room is full!"))

            elif data == "READY":
                if not room_code or room_code not in rooms:
                    continue

                if player_role == 1:
                    rooms[room_code][2] = True
                elif player_role == 2:
                    rooms[room_code][3] = True
                print(f"[ROOM {room_code}] Player {player_role} ready")
                print(rooms[room_code])

                if rooms[room_code][2] and rooms[room_code][3]:
                    p1, p2, *_ = rooms[room_code]
                    p1.sendall(str.encode("ROLE:1"))
                    p2.sendall(str.encode("ROLE:2"))
                    # p1.sendall(str.encode("START"))
                    # p2.sendall(str.encode("START"))
                    print(f"[ROOM {room_code}] Game started!")

            elif data == "CANCEL":
                if not room_code or room_code not in rooms:
                    continue
                if player_role == 1:
                    rooms[room_code][2] = False
                elif player_role == 2:
                    rooms[room_code][3] = False
                print(f"[ROOM {room_code}] Player {player_role} not ready")

            elif data.startswith("MOVE:"):
                broadcast(room_code, data, conn)
            elif data == "QUIT":
                broadcast(room_code, "LEFT", conn)
                break

            elif data == "LEAVE":
                break
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        conn.close()

        if room_code in rooms:
            if player_role == 1:
                rooms[room_code][0] = None
            elif player_role == 2:
                rooms[room_code][1] = None
            # Remove empty room
            if not rooms[room_code][0] and not rooms[room_code][1]:
                del rooms[room_code]

while True:
    conn, addr = s.accept()
    print(f"Connected to: {addr}")
    start_new_thread(threaded_client, (conn, addr))