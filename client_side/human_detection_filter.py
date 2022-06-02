from __future__ import print_function
from multiprocessing.pool import ThreadPool
from collections import deque
from datetime import datetime

import sys
sys.path.append('/home/ubuntu/human_detection/multi_thread/grpc_files')

import grpc_files.test_bluefield_4_pb2 as pb2
import grpc_files.test_bluefield_4_pb2_grpc as pb2_grpc

import pafy
import grpc
import logging
import cv2 as cv
import numpy as np

# Server IP
IP = 'SERVER_IP:50051'
FRAME = 0

# CAUTION!! The function needs a list of Rectangle type objects as parameter.
def send_to_cpu(current_frame, n_frame, process_time, rectangles):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be used
    # in circumstances in which the with statement does not fit the needs of the code

    logging.basicConfig()

    with grpc.insecure_channel(IP) as channel:
        stub = pb2_grpc.DetectionStub(channel)
        from_server = stub.SendFrame(pb2.Rectangles(frame=current_frame , num_frame=n_frame, time = process_time, detections=rectangles))
        return from_server

url  = "https://www.youtube.com/watch?v=XwXKJHgRM50"
#url = "https://www.youtube.com/watch?v=AdUw5RdyZxI"
#url = "https://www.abbeyroad.com/6f0394df-f3fc-4896-a2b7-18904518c544"

video = pafy.new(url)
best = video.getbest(preftype="mp4")

def clock(time=None):
    if not time:
        return datetime.now()
    return time

class DummyTask:
    def __init__(self, data):
        self.data = data
    def ready(self):
        return True
    def get(self):
        return self.data

if __name__ == '__main__':
    import sys
    print(__doc__)
    try:
        cap = cv.VideoCapture(sys.argv[1])
    except:
        cap = cv.VideoCapture(best.url)

    # OPencv HAAR algorithm for human recognition
    haar= cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_fullbody.xml')

    def process_frame(num_frame, frame):
        t0 = clock(T0)
        gray = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
        boxes = haar.detectMultiScale(gray, 1.1, 1)

        # 'boxes' is an Array of Rectangle type objects (Rectangle class is defined in .proto file)
        boxes = np.array( [pb2.Rectangle(r1=x, r2=y, r3=x+w, r4=y+h) for (x,y,w,h) in boxes] )
        t = clock() - t0

        if boxes.any():
            # CAUTION!! Send a whole frame using grpc is a very expensive operation!
            #current_frame = pb2.Frame(  lines=[pb2.Line( pixels=[pb2.Pixel(r=l1, g=l2, b=l3 ) for (l1,l2,l3) in line] ) for line in frame]  ) 
            current_frame = pb2.Frame(lines=[])
            from_server = send_to_cpu(current_frame, num_frame, str(t), boxes)
            print(from_server.response)
        else:
            print('No person detected')

    threadn = cv.getNumberOfCPUs()
    pool = ThreadPool(processes = threadn)
    pending = deque()

    threaded_mode = True
    T0 = datetime.now()
    while True:
        while len(pending) > 0 and pending[0].ready():
            res = pending.popleft().get()

        if len(pending) < threadn:
            ret, frame = cap.read()
            if frame is None:
                break

            FRAME += 1
            # Only odd frames are processed
            if FRAME % 2 == 0:
                continue
            else:
                pending.append( pool.apply_async(process_frame, (FRAME, frame.copy(), )) )
        ch = cv.waitKey(1)
        if ch == ord(' '):
            threaded_mode = not threaded_mode
        if ch == 27:
            break
    cv.destroyAllWindows()
