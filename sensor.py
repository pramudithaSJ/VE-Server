# import RPi.GPIO as GPIO
# import time

# # Define GPIO pins for the ultrasonic sensor
# TRIG_PIN = 21
# ECHO_PIN = 20

# # Set up GPIO mode
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(TRIG_PIN, GPIO.OUT)
# GPIO.setup(ECHO_PIN, GPIO.IN)

# class UltrasonicSensor:
#     @staticmethod
#     def get_distance():
#         # Ensure the trigger pin is low
#         GPIO.output(TRIG_PIN, False)
#         time.sleep(0.2)  # Delay to ensure sensor settles

#         # Trigger ultrasonic pulse
#         GPIO.output(TRIG_PIN, True)
#         time.sleep(0.00001)
#         GPIO.output(TRIG_PIN, False)

#         # Measure time for echo
#         pulse_start = None
#         pulse_end = None

#         # Wait for the echo to start
#         timeout_start = time.time()
#         while GPIO.input(ECHO_PIN) == 0:
#             pulse_start = time.time()
#             if time.time() - timeout_start > 0.1:  # Timeout after 0.1 seconds
#                 print("Timeout: No echo start detected")
#                 return None

#         # Wait for the echo to end
#         timeout_start = time.time()
#         while GPIO.input(ECHO_PIN) == 1:
#             pulse_end = time.time()
#             if time.time() - timeout_start > 0.1:  # Timeout after 0.1 seconds
#                 print("Timeout: No echo end detected")
#                 return None

#         if pulse_start is None or pulse_end is None:
#             print("Failed to detect echo")
#             return None

#         # Calculate distance in cm
#         pulse_duration = pulse_end - pulse_start
#         distance = pulse_duration * 17150
#         distance = round(distance, 2)
#         return distance

# try:
#     while True:
#         distance = UltrasonicSensor.get_distance()
#         if distance is not None:
#             print(f"Distance: {distance} cm")
#         else:
#             print("Error: Could not measure distance")
#         time.sleep(1)

# except KeyboardInterrupt:
#     print("Measurement stopped by user")

# finally:
#     GPIO.cleanup()
