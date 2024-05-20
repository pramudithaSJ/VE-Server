import json
import threading
import logging
from websocket_server import WebsocketServer
from walkingServer import WalkingServer
from mathServer import MathDetectionServer
from money_main import app
from scienceServer import ScienceDetectionServer
from activityServer import app

class MainServer:
    def __init__(self, host='0.0.0.0', port=9002):
        self.detection_server = WalkingServer()
        self.math_detection_server = MathDetectionServer()
        self.science_detection_server = ScienceDetectionServer()
        self.activity_server = app
        self.money_server = app
        self.server = WebsocketServer(host=host, port=port)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        self.clients = set()

        logging.basicConfig(level=logging.INFO)

    def new_client(self, client, server):
        self.clients.add(client['id'])
        logging.info(f"New client connected: {client['id']}")

    def client_left(self, client, server):
        if client['id'] in self.clients:
            self.clients.remove(client['id'])
        logging.info(f"Client disconnected: {client['id']}")

    def message_received(self, client, server, message):
        print(message)
        try:
            payload = json.loads(message)
            if 'mode' in payload and client['id'] in self.clients:
                if payload['mode'] == 'walking':
                    self.detection_server.run(client=client, server=server, message=message)
                elif payload['mode'] == 'math':
                    self.math_detection_server.run(client=client, server=server, message=message)
                elif payload['mode'] == 'science':
                    self.science_detection_server.run(client=client, server=server, message=message)
                elif payload['mode'] == 'activity':
                    self.activity_server.run()
                elif payload['mode'] == 'money':
                    self.money_server.run()

        except Exception as e:
            logging.error(f"Error processing message from client {client['id']}: {str(e)}")

    def run(self):
        thread = threading.Thread(target=self.server.run_forever)
        thread.start()
        try:
            thread.join()
        except KeyboardInterrupt:
            self.server.shutdown()
            logging.info("Server shutdown successfully.")

if __name__ == "__main__":
    main_server = MainServer()
    main_server.run()
