import numpy as np
import subprocess
import sys
import time
import cv2
# Start the C++ subprocess
proc = subprocess.Popen(['./multi_stream_app'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def send_data(data):
    """ Send data (either an integer or a numpy array) to the subprocess. """
    if isinstance(data, int):
        data_array = np.array([data], dtype=np.int32)
    elif isinstance(data, np.ndarray):
        data_array = data.astype(np.int8)
    else:
        raise ValueError("Unsupported data type")

    proc.stdin.write(data_array.tobytes())
    proc.stdin.flush()


def receive_data(data_type='int', size=1):
    """ Receive data from the subprocess and return it as the specified type. """
    nbytes = np.dtype(np.int32).itemsize * size
    output = proc.stdout.read(nbytes)
    if data_type == 'int':
        result = np.frombuffer(output, dtype=np.int32)
        return result[0] if size == 1 else result
    elif data_type == 'array':
        return np.frombuffer(output, dtype=np.int32)
    else:
        raise ValueError("Unsupported data type")

# Send initial configuration
num_of_streams = 1
send_data(num_of_streams)


# Open video file
cap = cv2.VideoCapture('../../input_images/detection.avi')
if not cap.isOpened():
    print("Error opening video file")
    sys.exit()

# send video size
send_data(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))*int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))*3)
# send_data(4*4*3)

# Read and send frames
while True:
    ret, frame = cap.read()
    if not ret:
        break  # Break the loop if no frames are left
    # re_frame = cv2.resize(frame, (4,4))
    # print("frame data type ",re_frame.dtype)
    # print("frame data type ",frame.dtype)
    # print('python ',re_frame)
    # print('python ',frame)
    
    # send_data(re_frame)
    send_data(frame)
    #break
    # time.sleep(1/30)  # Assume 30 fps, adjust according to your video file's frame rate

# Clean up video capture
cap.release()

time.sleep(3)

# Close the subprocess when done
proc.stdin.close()
proc.terminate()
proc.wait()
