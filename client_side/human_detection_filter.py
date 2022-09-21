from __future__ import print_function
from multiprocessing.pool import ThreadPool
from collections import deque
from datetime import datetime

import sys
sys.path.append('ADD PATH TO GRPC_FILES FOLDER HERE')

import grpc_files.test_bluefield_4_pb2 as pb2
import grpc_files.test_bluefield_4_pb2_grpc as pb2_grpc

import pafy
import grpc
import logging
import cv2 as cv
import numpy as np

# CAUTION! You must set the server IP. By default we are using port 50051.
# Check the port in server side if you change this value.
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

    # # OPencv HAAR algorithm for human recognition
    # First approach, human detection.
    # haar= cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_fullbody.xml')

    def frame_diff(num_frame, frame0, frame):
        t0 = clock(T0)
        gray0 = frame0
        gray  = frame

        differences = np.abs(gray0-gray)
        t = clock() - t0

        threshold = 10
        if np.count_nonzero(differences) > threshold :
            # CAUTION!! Send a whole frame using grpc is a very expensive operation!
            #current_frame = pb2.Frame(  lines=[pb2.Line( pixels=[pb2.Pixel(r=l1, g=l2, b=l3 ) for (l1,l2,l3) in line] ) for line in frame]  ) 

            current_frame = pb2.Frame(lines=[])
            from_server = send_to_cpu(current_frame, num_frame, str(t), [pb2.Rectangle(r1=0, r2=0, r3=0, r4=0)] )
            print(from_server.response)
        else:
            print('DIFF: ' , differences)


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
                print("TOTAL TIME: ", datetime.now()-T0 )
                break

            FRAME += 1
            # Only even frames are processed
            if FRAME % 2 != 0:
                frame0 = frame.copy() 
            else:
                pending.append( pool.apply_async(frame_diff, (FRAME, frame0, frame.copy(), )) )
        ch = cv.waitKey(1)
        if ch == ord(' '):
            threaded_mode = not threaded_mode
        if ch == 27:
            break
    cv.destroyAllWindows()
