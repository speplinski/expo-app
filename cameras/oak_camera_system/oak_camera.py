import depthai as dai
import time
import threading
from .camera_script_template import generate_script

class OakCamera:
    def __init__(self, config):
        self.name = config['name']
        self.ip_address = config['ip_address']
        self.nH, self.nV = config['grid_size']
        self.margin_T, self.margin_B, self.margin_L, self.margin_R = config['margins']
        self.port = config.get('port', 65432)
        self.retry_delay = config.get('retry_delay', 10)
        self.script_config = config.get('script_config', {})
        
        if 'port' not in self.script_config:
            self.script_config['port'] = self.port
        
        self.device = None
        self.pipeline = None
        self.running = False
        
    def _create_pipeline(self):
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
        
        rV = self.nV * 1.0 / (1.0 - (self.margin_T + self.margin_B))
        rH = self.nH * 1.0 / (1.0 - (self.margin_L + self.margin_R))
        
        for y in range(self.nV):
            for x in range(self.nH):
                config = dai.SpatialLocationCalculatorConfigData()
                config.depthThresholds.lowerThreshold = 200
                config.depthThresholds.upperThreshold = 10000
                config.roi = dai.Rect(
                    dai.Point2f(self.margin_R + x/rH, self.margin_T + y/rV), 
                    dai.Point2f(self.margin_R + (x+1)/rH, self.margin_T + (y+1)/rV)
                )
                spatialLocationCalculator.initialConfig.addROI(config)
        
        script = pipeline.create(dai.node.Script)
        script.setProcessor(dai.ProcessorType.LEON_CSS)
        
        script.inputs['spat'].setBlocking(False)
        script.inputs['spat'].setQueueSize(1)
        spatialLocationCalculator.out.link(script.inputs['spat'])
        
        script_code = generate_script(self.script_config)
        script.setScript(script_code)
        
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)
        stereo.depth.link(spatialLocationCalculator.inputDepth)
        
        self.pipeline = pipeline
        return pipeline
    
    def start(self):
        if self.running:
            print(f"Camera {self.name} ({self.ip_address}) is already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run_camera)
        self._thread.daemon = True
        self._thread.start()
        return self._thread
    
    def _run_camera(self):
        while self.running:
            try:
                if not self.pipeline:
                    self._create_pipeline()
                
                d_info = dai.DeviceInfo(self.ip_address)
                with dai.Device(self.pipeline, deviceInfo=d_info) as device:
                    self.device = device
                    print(f"Connected to camera {self.name} ({self.ip_address})")
                    
                    while not device.isClosed() and self.running:
                        time.sleep(1)
                
                self.device = None
                
            except Exception as e:
                print(f"Error with camera {self.name} ({self.ip_address}): {e}")
                print(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
    
    def stop(self):
        self.running = False
        if self.device:
            self.device.close()
        if hasattr(self, '_thread'):
            self._thread.join(timeout=5)
            print(f"Camera {self.name} ({self.ip_address}) stopped")
            
    def get_status(self):
        if not self.running:
            return f"Camera {self.name} ({self.ip_address}): Stopped"
        elif self.device:
            return f"Camera {self.name} ({self.ip_address}): Connected and running"
        else:
            return f"Camera {self.name} ({self.ip_address}): Attempting to connect"