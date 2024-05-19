import json , time
from flask import Flask, jsonify, request, make_response
from ultralytics import YOLO
import cv2
from postprocessing import *
import collections,numpy
import random
import uuid
from datetime import datetime

money_model = YOLO("models/money.pt")
money_class_list = money_model.model.names
scale_show = 100

def show_image(image):
    cv2.imshow("Image", image)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response
@app.route('/main', methods=['POST'])
def main():
    
        request_data = request.get_json()
        print(request_data)
        full_amount = int(request_data['full_amount'])

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        ret, frame = cap.read()

        results = money_model.predict(frame)
        labeled_img = draw_box(frame, results[0], money_class_list)
        display_img = resize_image(labeled_img, scale_show)

        unique_id = str(uuid.uuid4())
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        image_path = 'output/'+f"{timestamp}_{unique_id}.jpg"

        cv2.imwrite(image_path,display_img)

        image = cv2.imread(image_path)
        
        tem_array=numpy.array(results[0].boxes.cls.numpy().astype(int))
        counter = collections.Counter(tem_array)
        rs1=counter[0]
        rs10=counter[1]
        rs100=counter[2]
        rs1000=counter[3]
        rs2=counter[4]
        rs20=counter[5]
        rs5=counter[6]
        rs50=counter[7]
        rs500=counter[8]
        rs5000=counter[9]
        print(str(counter[0])+" 1 ruppees")
        print(str(counter[1])+" 10 ruppees")
        print(str(counter[2])+" 100 ruppees")
        print(str(counter[3])+" 1000 ruppees")
        print(str(counter[4])+" 2 ruppees")
        print(str(counter[5])+" 20 ruppees")
        print(str(counter[6])+" 5 ruppees")
        print(str(counter[7])+" 50 ruppees")
        print(str(counter[8])+" 500 ruppees")
        print(str(counter[9])+" 5000 ruppees")

        image_amount = (1*rs1)+(10*rs10)+(100*rs100)+(1000*rs1000)+(2*rs2)+(20*rs20)+(5*rs5)+(50*rs50)+(500*rs500)+(5000*rs5000)

        results=""

        if(full_amount==int(image_amount)):
            results="Your Answer Is Correct"
        elif(full_amount>int(image_amount)):
            results="Your Answer Is Incorrect Please Add more Money and try again"
        else:
            results="Your Answer Is Incorrect Your Money Amount Exceeded.Please try again"

        json_dump = json.dumps({"results":results,"success":"true"})

        cap.release()
        #show_image(image)

        return json_dump
        

@app.route('/one', methods=['GET'])
def one():
    
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        ret, frame = cap.read()

        results = money_model.predict(frame)
        labeled_img = draw_box(frame, results[0], money_class_list)
        display_img = resize_image(labeled_img, scale_show)

        unique_id = str(uuid.uuid4())
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        image_path = 'output/'+f"{timestamp}_{unique_id}.jpg"

        cv2.imwrite(image_path,display_img)

        image = cv2.imread(image_path)
        
        tem_array=numpy.array(results[0].boxes.cls.numpy().astype(int))
        counter = collections.Counter(tem_array)
        rs1=counter[0]
        rs10=counter[1]
        rs100=counter[2]
        rs1000=counter[3]
        rs2=counter[4]
        rs20=counter[5]
        rs5=counter[6]
        rs50=counter[7]
        rs500=counter[8]
        rs5000=counter[9]
        print(str(counter[0])+" 1 ruppees")
        print(str(counter[1])+" 10 ruppees")
        print(str(counter[2])+" 100 ruppees")
        print(str(counter[3])+" 1000 ruppees")
        print(str(counter[4])+" 2 ruppees")
        print(str(counter[5])+" 20 ruppees")
        print(str(counter[6])+" 5 ruppees")
        print(str(counter[7])+" 50 ruppees")
        print(str(counter[8])+" 500 ruppees")
        print(str(counter[9])+" 5000 ruppees")

        image_amount = (1*rs1)+(10*rs10)+(100*rs100)+(1000*rs1000)+(2*rs2)+(20*rs20)+(5*rs5)+(50*rs50)+(500*rs500)+(5000*rs5000)

        json_dump = json.dumps({"results":str(image_amount),"success":"true"})

        cap.release()
        #show_image(image)

        return json_dump

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
	app.run(host="0.0.0.0", port=5555)