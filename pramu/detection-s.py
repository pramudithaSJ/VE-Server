import cv2
import json
import base64
import threading
from ultralytics import YOLO
from websocket_server import WebsocketServer
import torch
from camera import Camera

class DetectionServer:
    def __init__(self, host='0.0.0.0', port=9001):
        self.server = WebsocketServer(host=host, port=port)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.current_model_path = './models/walking-model.pt'  # Default model path
        self.model = self.load_model(self.current_model_path)
        self.detection_active = False
        self.client_connected = False
        
    def load_model(self, model_path):
        model = YOLO(model_path).to(self.device)
        print(f"Model loaded: {model_path}")
        return model
    
    def new_client(self, client, server):
        if self.client_connected:  # Check if a client is already connected
            server.send_message(client, json.dumps(
                {"error": "Server is already in use."}))
            server.server_close_client(client['id'])
        else:
            self.client_connected = True
            print(f"New client connected: {client['id']}")

    def client_left(self, client, server):
        self.client_connected = False
        self.detection_active = False
        print(f"Client disconnected: {client['id']}")
    
    def detect_objects(self, frame):
        results = self.model(frame)[0]
        
        for result in results:
            boxes = result.boxes.data.cpu().numpy(
            ) if torch.cuda.is_available() else result.boxes.data.numpy()
            for box in boxes:
                x1, y1, x2, y2, confidence, label_id = box[:6]
                label = self.model.names[int(label_id)]
                key = f"{label}"
