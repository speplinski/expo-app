import depthai as dai

# ToDo: check if still works after mixing nodes linking with other instructions instead of linking at the end
def build_oak_d_pipeline(
        horizontal_segments_count, vertical_segments_count,
        lower_depth_threshold, upper_depth_threshold
):
    pipeline = dai.Pipeline()

    stereo = _build_stereo(pipeline)
    spatial_location_calculator = _build_spatial_location_calculator(pipeline)

    xin_spatial_calc_config = pipeline.create(dai.node.XLinkIn)
    xin_spatial_calc_config.setStreamName("spatialCalcConfig")

    for y in range(vertical_segments_count):
        for x in range(horizontal_segments_count):
            config = dai.SpatialLocationCalculatorConfigData()
            config.depthThresholds.lowerThreshold = lower_depth_threshold
            config.depthThresholds.upperThreshold = upper_depth_threshold
            config.roi = dai.Rect(
                dai.Point2f(x / horizontal_segments_count, y / vertical_segments_count),
                dai.Point2f((x + 1) / horizontal_segments_count, (y + 1) / vertical_segments_count)
            )
            spatial_location_calculator.initialConfig.addROI(config)

    xin_spatial_calc_config.out.link(spatial_location_calculator.inputConfig)
    stereo.depth.link(spatial_location_calculator.inputDepth)

    return pipeline

def _build_stereo(pipeline):
    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_left.setCamera('left')

    mono_right = pipeline.create(dai.node.MonoCamera)
    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setCamera('right')

    stereo = pipeline.create(dai.node.StereoDepth)
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
    stereo.setLeftRightCheck(True)
    stereo.setSubpixel(True)

    mono_left.out.link(stereo.left)
    mono_right.out.link(stereo.right)

    return stereo

def _build_spatial_location_calculator(pipeline):
    spatial_location_calculator = pipeline.create(dai.node.SpatialLocationCalculator)
    spatial_location_calculator.inputConfig.setWaitForMessage(False)

    xout_depth = pipeline.create(dai.node.XLinkOut)
    xout_depth.setStreamName("depth")

    xout_spatial_data = pipeline.create(dai.node.XLinkOut)
    xout_spatial_data.setStreamName("spatialData")

    spatial_location_calculator.passthroughDepth.link(xout_depth.input)
    spatial_location_calculator.out.link(xout_spatial_data.input)

    return spatial_location_calculator