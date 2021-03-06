# DPU-HumanDetection

In this project we are using a BlueField DPU to detect people in a video file or stream. This is our first approach to using BlueField cards as a network layer prefilter to relieve the server of some heavy tasks. We are using grpc for communication between client and server. 
The whole project is written in Python.

Installation instructions:

    * Dependencies:
        OpenCV
        NumPy
        Pafy
        grpc
        logging

    You only have to place the correct files in client (DPU in our case) and server machines:
    
    * Client needs:
        - human_detection_filter.py (You must set the server IP. Also check the route to the 'grpc_files' folder)
        - grpc_files folder
        - multimedia folder
    * Server needs:
        - server.py (Check the route to the 'grpc_files' folder in your machine)
        - grpc_files folder

    Once you have copied the files just run server.py in server side and then run human_detection_filter.py in client side

Note: human_detection_filter.py accept one argument (a string with the route to a video file) you can use the video in multimedia folder to do your test. It is also possible to use a streaming url. If you do not use this argument, a default streaming will be used.
    