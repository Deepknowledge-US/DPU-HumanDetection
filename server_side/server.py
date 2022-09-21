from concurrent import futures
import grpc
import logging
import grpc_files.test_bluefield_4_pb2 as pb2
import grpc_files.test_bluefield_4_pb2_grpc as pb2_grpc

class Detection(pb2_grpc.DetectionServicer):
    def SendFrame(self, request, context):
        print('\nFrame:', str(request.num_frame),'\n\tDetection: ', request.detections)

        # At this point we need to call the weapons detection model. 
        # You can access the frame identifier via request.num_frame.
        # When using a human detection model, we can also pass the 
        # bounding box of the detections to the server using the request.detections variable.

        return pb2.Empty(response=request.num_frame)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_DetectionServicer_to_server(Detection(), server)
    server.add_insecure_port('[::]:50051')   # By default we are using port 50051
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()