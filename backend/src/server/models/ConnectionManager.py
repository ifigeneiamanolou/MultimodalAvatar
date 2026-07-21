from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections : list[WebSocket] = []

    async def connect(self, connection : WebSocket):
        await connection.accept()
        self.active_connections.append(connection)

    async def disconnect(self, connection : WebSocket):
        self.active_connections.remove(connection)

    async def send_personal(self, connection : WebSocket, data : str):      # Send data to a single client 
        await connection.send_text(data)

    async def broadcast(self, data : str):                                  # Send data to all clients connected to the server
        for connection in self.active_connections:
            await connection.send_text(data)

