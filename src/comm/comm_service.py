import socket
import threading
import json
import uuid
from typing import Dict, Any, Callable
import asyncio
import logging

from comm.messages.message_base import InitContinuesRegistrationResponse, MessageBase, MessageTypes

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


class CommunicationService:
    """Async TCP Communication Service"""
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def start_server(self):
        """Start TCP server"""
        self.server_socket = await asyncio.start_server(
            self.handle_client, self.host, self.port)
        
        addr = self.server_socket.sockets[0].getsockname()
        self.logger.info(f'Serving on {addr}')
        
        async with self.server_socket:
            await self.server_socket.serve_forever()

    async def connect_client(self):
        """Connect as a client"""
        try:
            self.client_socket = await asyncio.open_connection(
                self.host, self.port)
            self.logger.info(f'Connected to {self.host}:{self.port}')
            
            # Start receiving messages
            await self.receive_messages()
        except Exception as e:
            self.logger.error(f"Connection error: {e}")

    async def handle_client(self, reader: asyncio.StreamReader, 
                            writer: asyncio.StreamWriter):
        """Handle incoming client connections"""
        addr = writer.get_extra_info('peername')
        self.logger.info(f'Received connection from {addr}')
        
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                
                message = data.decode()
                await self.process_message(message, writer)
        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
        finally:
            writer.close()

    async def process_message(self, message: str, 
                               writer: asyncio.StreamWriter = None):
        """Process incoming messages"""
        try:
            msg_dict = json.loads(message)
            msg_type = msg_dict.get('type')
            msg_id = msg_dict.get('id')

            # Check if it's a response to a previous request
            if msg_id in self.pending_responses:
                future = self.pending_responses.pop(msg_id)
                future.set_result(msg_dict)
                return

            # Handle message via registered handlers
            if msg_type in self.message_handlers:
                handler = self.message_handlers[msg_type]
                response = await handler(msg_dict)
                
                # Send response back if possible
                if writer and response:
                    response_json = json.dumps(response)
                    writer.write(response_json.encode())
                    await writer.drain()
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")

    async def send_message(self, message: MessageBase):
        """Send message and wait for response"""
        try:
            # Create future for response tracking
            future = asyncio.Future()
            self.pending_responses[message.id] = future
            
            # Send message
            message_json = json.dumps(message.__dict__)
            reader, writer = self.client_socket
            writer.write(message_json.encode())
            await writer.drain()

            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=10.0)
            return response
        except asyncio.TimeoutError:
            self.logger.error("Message send timeout")
        except Exception as e:
            self.logger.error(f"Message send error: {e}")

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler

    async def receive_messages(self):
        """Continuously receive messages"""
        reader, _ = self.client_socket
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                message = data.decode()
                await self.process_message(message)
        except Exception as e:
            self.logger.error(f"Message receive error: {e}")

# Example Usage
async def example_usage():
    # Server-side example
    server = CommunicationService(port=8000)
    
    # Define a handler for a specific message type
    async def handle_init_registration(message):
        print("Received registration request:", message)
        return InitContinuesRegistrationResponse(
            success=True, 
            error_message=""
        )
    
    server.register_handler(
        MessageTypes.INIT_CONTINUES_REGISTRATION_REQUEST, 
        handle_init_registration
    )

    # Start server in background
    server_task = asyncio.create_