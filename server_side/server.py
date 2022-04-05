from concurrent import futures
import grpc
import logging
import test_bluefield_4_pb2 as pb2
import test_bluefield_4_pb2_grpc as pb2_grpc

class Detection(pb2_grpc.DetectionServicer):
    def SendFrame(self, request, context):
        print('\nFrame:', str(request.num_frame),'\n\tDetection: ', request.detections)
        return pb2.Empty(response=request.num_frame)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_DetectionServicer_to_server(Detection(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
