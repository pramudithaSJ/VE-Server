import json
import cv2
import logging
from ultralytics import YOLO
import supervision as sv
from flask import Flask, request, jsonify
import random
from flask_cors import CORS

def random_data1():
    price_array1 = [20,40,50,60,80,100,200]
    price_array2 = [50,100,1000,5000]
    x=random.choice(price_array1)
    y=random.choice(price_array2)
    
    if(y>x):
        return x,y
    else:
        return random_data1()
    
def random_data2():
    price_array1 = [20,40,50,60,80,100,200]
    price_array2 = [50,100,1000,5000]
    x=random.choice(price_array1)
    y=random.randint(1, 20)
    z=random.choice(price_array2)
    
    if((x*y)<z):
        return x,y,z
    else:
        return random_data2()
    
def random_data3():
    price_array1 = [200,500,800,1000,3000,5000]
    x=random.choice(price_array1)
    y=random.randint(1, 10)
    
    if(x%y==0):
        return x,y
    else:
        return random_data3()
    
    
app = Flask(__name__)
CORS(app)

class ActivityServer:
    def __init__(self):
        self.detected_notes = []
        self.json_sink_path = "detected_notes.json"
        self.cap = None
        self.yolo = None

    def initialize_resources(self):
        self.cap = cv2.VideoCapture(0)
        self.yolo = YOLO("models/money.pt")
        logging.info("Detection resources initialized")

    def detect(self):
        self.initialize_resources()
        logging.info("Starting detection")

        while True:
            success, frame = self.cap.read()
            if not success:
                logging.error("Failed to read frame from camera")
                self.release_resources()
                return jsonify({"message": "Failed to read frame from camera"}), 500

            results = self.yolo(frame)[0]
            logging.info(f"YOLO results: {results}")
            detections = sv.Detections.from_ultralytics(results)
            logging.info(f"Detections: {detections}")
            detections = detections[detections.confidence > 0.70]

            if len(detections) > 0:
                logging.info("High confidence detections found")
                if hasattr(detections, 'class_name') and detections['class_name'] is not None:
                    labels = [
                        class_name.split()[0]  # Extract just the numeric part
                        for class_name in detections['class_name']
                    ]
                else:
                    logging.warning("No 'class_name' in detections or 'class_name' is None")
                    labels = []

                self.release_resources()
                return jsonify({"message": "High confidence detections found", "data": labels}), 200
            else:
                logging.info("No high confidence detections found")
                self.release_resources()
                return jsonify({"message": "No high confidence detections found"}), 200
                
                                

    def release_resources(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            return jsonify({"message": "Resources released"}), 200
        if self.yolo:
            del self.yolo
        logging.info("Detection resources released")

    def calculate_total(self):
        note_values = {
            '10': 10,
            '20': 20,
            '50': 50,
            '100': 100,
            '500': 500,
            '1000': 1000,
            '2000': 2000,
            '5000': 5000
        }

        total_amount = sum(note_values[note] for note in self.detected_notes if note in note_values)
        total_message = {"type": "total", "message": "Total amount calculated", "total_amount": total_amount}

        # Reset detected notes for the next session
        self.detected_notes = []

        return jsonify(total_message), 200

activity_server = ActivityServer()

@app.route('/detect', methods=['GET'])
def detect():
    return activity_server.detect()

@app.route('/stop', methods=['GET'])
def stop():
    return activity_server.release_resources()

@app.route('/question', methods=['GET'])
def question():
    
    try:
        x1=random.randint(1, 20)
        price_array = [20,40,50,60,80,100]
        y1=random.choice(price_array)
        result1=x1*y1
        q1="If a mango is "+str(y1)+" rupees, how much money is needed to buy "+str(x1)+" mangoes?"

        x2,y2=random_data1()
        result2=y2-x2
        q2="If the price of a loaf of bread is "+str(x2)+" rupees, what is the remaining amount when "+str(y2)+" rupees are given?"

        price_array = [1,2,5,10]
        x3=random.choice(price_array)
        price_array = [2,5,15,1,20]
        y3=random.choice(price_array)
        z3=random.randint(1, 10)
        w3=random.randint(1, 20)
        result3=(x3*z3)+(y3*w3)
        q3="If a mango toffee costs Rs "+str(y3)+" and an apple toffee costs Rs "+str(y3)+", how much money is required to buy "+str(z3)+" mango toffees and "+str(w3)+" apple toffees?"

        price_array = [10,20,50,100]
        x4=random.choice(price_array)
        y4=random.randint(1, 20)
        result4=(x4*y4)
        q4="If an apple costs "+str(x4)+" rupees, what is the price of "+str(y4)+" apples?"

        x5,y5,z5=random_data2()
        result5=z5-(x5*y5)
        q5="If the price of a pineapple is "+str(x5)+" rupees, what is the remaining amount when you give "+str(z5)+" rupees to buy "+str(y5)+" pineapple?"

        price_array = [50,100,500,1000]
        x6=random.choice(price_array)
        price_array = [50,100,5000]
        y6=random.choice(price_array)
        result6=x6+y6
        q6="Kasun has about "+str(x6)+" rupees. Malith has "+str(y6)+". What is the closest sum to the two?"

        price_array = [100,1000,5000,500,200,3000,1200]
        x7=random.choice(price_array)
        result7=x7/2
        q7="There is a concession of Rs. "+str(x7)+". How much money will he have left when he gives half of the money to his friend?"
        
        price_array = [1000,5000,3000,1200]
        x8=random.choice(price_array)
        price_array = [200,100,400,800,600]
        y8=random.choice(price_array)
        result8=x8-y8
        q8="Saduni has Rs. "+str(x8)+". When she gives "+str(y8)+" rupees to Sachini, how much money does she have left?"

        x9,y9=random_data3()
        result9=x9/y9
        q9="Amal has Rs."+str(x9)+". If that amount is divided equally among "+str(y9)+" people, how much will each person get?"

        price_array = [2000,1500,3000,2500]
        x10=random.choice(price_array)
        price_array = [1200,500,800,1000]
        y10=random.choice(price_array)
        result10=x10-y10
        q10="Kasun has Rs. "+str(x10)+". If Kasun spent "+str(y10)+" rupees out of that amount, what is the remaining amount?"

        q_number=random.choice([5,10,4,6,9,7,8])
        print(q_number)

        if(q_number==1):
            json_dump = json.dumps({"question":q1,"answer":str(result1),"success":"true"})

            return json_dump
        elif(q_number==2):
            json_dump = json.dumps({"question":q2,"answer":str(result2),"success":"true"})

            return json_dump
        elif(q_number==3):
            json_dump = json.dumps({"question":q3,"answer":str(result3),"success":"true"})

            return json_dump
        elif(q_number==4):
            json_dump = json.dumps({"question":q4,"answer":str(result4),"success":"true"})

            return json_dump
        elif(q_number==5):
            json_dump = json.dumps({"question":q5,"answer":str(result5),"success":"true"})

            return json_dump
        elif(q_number==6):
            json_dump = json.dumps({"question":q6,"answer":str(result6),"success":"true"})

            return json_dump
        elif(q_number==7):
            json_dump = json.dumps({"question":q7,"answer":str(result7),"success":"true"})

            return json_dump
        elif(q_number==8):
            json_dump = json.dumps({"question":q8,"answer":str(result8),"success":"true"})

            return json_dump
        elif(q_number==9):
            json_dump = json.dumps({"question":q9,"answer":str(result9),"success":"true"})

            return json_dump
        else:
            json_dump = json.dumps({"question":q10,"answer":str(result10),"success":"true"})

            return json_dump
        
    except:
        json_dump = json.dumps({"success":"false"})

        return json_dump


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
