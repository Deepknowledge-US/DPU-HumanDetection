# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function

import logging

import grpc
import test_bluefield_pb2
import test_bluefield_pb2_grpc


def run(rectangles):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be used
    # in circumstances in which the with statement does not fit the needs of the code

    ip = '94.188.142.138:50051'
    with grpc.insecure_channel(ip) as channel:
        stub = test_bluefield_pb2_grpc.DetectionStub(channel)
        response = stub.SendFrame(test_bluefield_pb2.Rectangles(detections=rectangles))
    print("Message from server received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    rec1 = test_bluefield_pb2.Rectangle(r1=2, r2=4, r3=6, r4=8)
    rec2 = test_bluefield_pb2.Rectangle(r1=1, r2=3, r3=5, r4=7)
    recs = [rec1, rec2]
    run(recs)
