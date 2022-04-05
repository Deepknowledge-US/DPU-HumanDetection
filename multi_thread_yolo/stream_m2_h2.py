from __future__ import print_function
from multiprocessing.pool import ThreadPool
from collections import deque
from datetime import datetime

import sys
sys.path.append('/home/ubuntu/human_detection/multi_thread/grpc_files')

import test_bluefield_2_pb2 as pb2
import test_bluefield_2_pb2_grpc as pb2_grpc

import pafy
import grpc
import logging
import cv2 as cv
import numpy as np

IP = '94.188.142.138:50051'
FRAME = 0

# CAUTION!! The function needs a list of Rectangle type objects as parameter.
def send_to_cpu(num_frame, rectangles):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be used
    # in circumstances in which the with statement does not fit the needs of the code

    logging.basicConfig()

    with grpc.insecure_channel(IP) as channel:
        stub = pb2_grpc.DetectionStub(channel)
        from_server = stub.SendFrame(pb2.Rectangles(frame=num_frame, detections=rectangles))
        return from_server

url = "https://www.youtube.com/watch?v=AdUw5RdyZxI"
#url = "https://www.abbeyroad.com/6f0394df-f3fc-4896-a2b7-18904518c544"
video = pafy.new(url)
best = video.getbest(preftype="mp4")

def clock():
    return datetime.now()

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
        fn = sys.argv[1]
    except:
        fn = 0

    cap = cv.VideoCapture(best.url)
    haar= cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_fullbody.xml')

    def process_frame(num_frame, frame):
        t0 = clock()
        gray = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
        boxes = haar.detectMultiScale(gray, 1.1, 1)
#        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
        boxes = np.array( [pb2.Rectangle(r1=x, r2=y, r3=x+w, r4=y+h) for (x,y,w,h) in boxes] )
        t = clock() -t0

        if boxes.any():
            from_server = send_to_cpu(num_frame, boxes)
            print(from_server.response)
        else:
            print('No person detected')

###############################

    threadn = cv.getNumberOfCPUs()
    pool = ThreadPool(processes = threadn)
    pending = deque()

    threaded_mode = True

    while True:
        while len(pending) > 0 and pending[0].ready():
            res = pending.popleft().get()

        if len(pending) < threadn:
            ret, frame = cap.read()
            if frame is None:
                break

# Append process_frame task to the pool
            FRAME += 1
            pending.append( pool.apply_async(process_frame, (FRAME, frame.copy(), )) )

        ch = cv.waitKey(1)
        if ch == ord(' '):
            threaded_mode = not threaded_mode
        if ch == 27:
            break
    cv.destroyAllWindows()
