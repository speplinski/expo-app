import depthai as dai
import time
import sys

nH = 22
nV = 14

OAK_IP = "192.168.70.65"

Margin_T = 0.1
Margin_B = 0.0
Margin_L = 0.25
Margin_R = 0.35

pipeline = dai.Pipeline()

monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
spatialLocationCalculator = pipeline.create(dai.node.SpatialLocationCalculator)

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setCamera("left")
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setCamera("right")

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
stereo.setLeftRightCheck(True)
stereo.setSubpixel(True)
spatialLocationCalculator.inputConfig.setWaitForMessage(False)

rV = nV*1.0/(1.0-(Margin_T+Margin_B))
rH = nH*1.0/(1.0-(Margin_L+Margin_R))
for y in range(nV):
    for x in range(nH):
        config = dai.SpatialLocationCalculatorConfigData()
        config.depthThresholds.lowerThreshold = 200
        config.depthThresholds.upperThreshold = 10000
        config.roi = dai.Rect(dai.Point2f(Margin_R + x/rH, Margin_T + y/rV), dai.Point2f(Margin_R + (x+1)/rH, Margin_T + (y+1)/rV))
        spatialLocationCalculator.initialConfig.addROI(config)

script = pipeline.create(dai.node.Script)
script.setProcessor(dai.ProcessorType.LEON_CSS)

script.inputs['spat'].setBlocking(False)
script.inputs['spat'].setQueueSize(1)
spatialLocationCalculator.out.link(script.inputs['spat'])

script.setScript("""
import socket
import random
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(('0.0.0.0', 65432)) 
server.listen(10)

while True:
    data = node.io['spat'].get()
    spatialData = data.getSpatialLocations()

    # Extract distances
    distances = []
    for depthData in spatialData:
        distance = depthData.spatialCoordinates.z / 1000  # Convert to meters
        distances.append(distance)
                    
    if len(distances) > 0 : 
        
        det_arr = []
        for det in distances:
            det_arr.append(f"{det:.1f}")
        det_str = "|".join(det_arr)
        
        #node.warn(f"Waiting for client")
        conn, client = server.accept()
        #node.warn(f"Connected to client IP: {client}")

        with conn:

            HLEN = 32
            MESLEN = len(det_str)
            header = f"HEAD {MESLEN}".ljust(HLEN)
            #node.warn(f'>{header}<')
            
            # send header
            msg = bytes(header, encoding='ascii')
            conn.sendall(msg)

            # send data
            msg = bytes(det_str, encoding='ascii')
            conn.sendall(msg)
""")

monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)
stereo.depth.link(spatialLocationCalculator.inputDepth)

d_info = dai.DeviceInfo(OAK_IP)

RETRY_DELAY = 10

while True:
    try:
        with dai.Device(pipeline, deviceInfo=d_info) as device:
            print(f"Connected to camera {OAK_IP}")
            
            while not device.isClosed():
                time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)