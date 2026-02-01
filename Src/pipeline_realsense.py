import pyrealsense2 as rs
import numpy as np
import cv2

class wlsFilter:
    wlsStream = "wlsFilter"
    def __init__(self, _lambda, _sigma):
        self._lambda = _lambda
        self._sigma = _sigma
        self.wlsFilter = cv2.ximgproc.createDisparityWLSFilterGeneric(False)
        cv2.namedWindow(self.wlsStream)
        #self.lambdaTrackbar = trackbar('Lambda', self.wlsStream, 0, 255, 80, self.on_trackbar_change_lambda)
        #self.sigmaTrackbar  = trackbar('Sigma',  self.wlsStream, 0, 100, 15, self.on_trackbar_change_sigma)

    def filter(self, disparity, right, depthScaleFactor):
        # https://github.com/opencv/opencv_contrib/blob/master/modules/ximgproc/include/opencv2/ximgproc/disparity_filter.hpp#L92
        self.wlsFilter.setLambda(self._lambda)
        # https://github.com/opencv/opencv_contrib/blob/master/modules/ximgproc/include/opencv2/ximgproc/disparity_filter.hpp#L99
        self.wlsFilter.setSigmaColor(self._sigma)
        filteredDisp = self.wlsFilter.filter(disparity, right)

        # Compute depth
        with np.errstate(divide='ignore'): 
            # raw depth values
            depthFrame = (depthScaleFactor / filteredDisp).astype(np.uint16)

        return filteredDisp, depthFrame

# Function to calculate the distance at a specific pixel
def get_pixel_distance(depth_frame, x, y):
    depth_value = depth_frame.get_distance(x, y)
    if depth_value:
        return round(depth_value, 2)
    else:
        return None

# Function to add circles and distance text for center, right, and left pixels
def add_circles_and_distances(image, depth_frame):
    height, width = image.shape[:2]
    
    # Center pixel & distance
    center_x, center_y = width // 2, height // 2
    center_distance = get_pixel_distance(depth_frame, center_x, center_y)
    cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)

    return center_x, center_y, center_distance

def mouse_move(event, x, y, flags, params):
   # x, y = event.xdata, event.ydata
    if event == cv2.EVENT_LBUTTONDOWN: 
        distance=  (get_pixel_distance(depth_frame,np.int32(x), np.int32(y)))
        if distance is not None:
            cv2.setWindowTitle("depth", "RealSense | Distance: %sm" %
            (distance))
        else:
            cv2.setWindowTitle("depth", "RealSense | Distance: %s" %
            ("no data"))
def save_pfm(filename, image, scale=1):
    """
    Save a matrix as a PFM (Portable Float Map) file.
    
    Args:
        filename (str): The name of the output PFM file.
        image (numpy.ndarray): The image data (2D or 3D array).
        scale (float): Scale factor. Use -1 for little-endian, +1 for big-endian.
    """
    with open(filename, 'wb') as f:
        # Determine the color format
        if image.ndim == 3 and image.shape[2] == 3:  # Color image
            color = True
        elif image.ndim == 2:  # Grayscale image
            color = False
        else:
            raise ValueError("Image must be a 2D (grayscale) or 3D (RGB) array.")

        # Write the header
        f.write(b'PF\n' if color else b'Pf\n')
        f.write(f"{image.shape[1]} {image.shape[0]}\n".encode())

        # Write the scale (negative for little-endian)
        endian = image.dtype.byteorder
        if endian == '<' or (endian == '=' and np.little_endian):
            scale = -scale
        f.write(f"{scale}\n".encode())

        # Write the image data
        image = np.flipud(image)  # Flip vertically because PFM uses bottom-left origin
        image.tofile(f)
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()

pc = rs.pointcloud()
# We want the points object to be persistent so we can display the last cloud when a frame drops
points = rs.points()

"""
Load from saved frame
rs.config.enable_device_from_file(config, "data_frame10.bag")


"""
# rs.config.enable_device_from_file(config, "06-03-2024 data collection/Scenario3/E6/data_frame1229.bag")

# Declare RealSense pipeline, encapsulating the actual device and sensors

# Enable depth stream
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.infrared, 1,1280, 720, rs.format.y8,30)
config.enable_stream(rs.stream.infrared, 2,1280, 720, rs.format.y8,30)
device_product_line = str(device.get_info(rs.camera_info.product_line))

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
# Start streaming with chosen configuration
profile = pipeline.start(config)

# We'll use the colorizer to generate texture for our PLY
# (alternatively, texture can be obtained from color or infrared stream)
colorizer = rs.colorizer()
colorizer.set_option(rs.option.min_distance, 0.1)
colorizer.set_option(rs.option.max_distance, 2)
decimation_filter = rs.decimation_filter()
spatial_filter = rs.spatial_filter()
temporal_filter = rs.temporal_filter()
threshold_filter = rs.threshold_filter()
wlsFilter = wlsFilter(_lambda=8000, _sigma=1.5)
import pyautogui
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale_RS = depth_sensor.get_depth_scale()
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

distance = 0
try:
    cv2.setWindowTitle("depth", "RealSense")
    while True:
    # Wait for the next set of frames from the camera
        frames = pipeline.wait_for_frames()
        filtered_frame = decimation_filter.process(frames)
        filtered_frame = spatial_filter.process(filtered_frame)
        filtered_frame = temporal_filter.process(filtered_frame)
        filtered_frame = threshold_filter.process(filtered_frame)

        filtered_frame = colorizer.process(filtered_frame)

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        IR_frame = frames.get_infrared_frame(1)
        IR1_frame = frames.get_infrared_frame(2)

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        IR_frame = np.asanyarray(IR_frame.get_data())
        IR1_frame = np.asanyarray(IR1_frame.get_data())

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.05),  cv2.COLORMAP_INFERNO)
        # gray =  cv2.cvtColor(depth_colormap,cv2.COLOR_RGB2GRAY)
        #     # Apply wls filter
        # filteredDisp, depthFrame = wlsFilter.filter(disparity= gray, right=IR_frame, depthScaleFactor=depth_scale_RS)
        # coloredDisp = cv2.applyColorMap(cv2.convertScaleAbs(filteredDisp, alpha=0.5),  cv2.COLORMAP_INFERNO)
        # plt.connect('motion_notify_event', mouse_move)
        #
        # cv2.setWindowTitle("depth", "RealSense (%dx%d) Distance: %dm" %
        # (w, h,distance))
        # added_image = cv2.addWeighted(color_image,0.4,depth_colormap,0.7,0)
        distance_pfm = np.zeros((depth_image.shape[0],depth_image.shape[1]))
        for i in range(depth_image.shape[0]):
            for j in range(depth_image.shape[1]):
                distance_pfm[i,j]=depth_frame.get_distance(j,i)
        # depth_image_normalized = cv2.normalize(depth_image, None, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        # depth_image_255 = (depth_image_normalized * 255).astype(np.uint8)
        # depth_image=depth_image/np.max(depth_image)
        max_distance = 2
        depth_image_clipped = np.where(depth_image * depth_frame.get_units() > max_distance, 0, depth_image)

        # Normalize depth image for visualization (optional)
        depth_image_normalized = cv2.normalize(depth_image_clipped, None, 0, 255, cv2.NORM_MINMAX)
        depth_image_8bit = depth_image_normalized.astype(np.uint8)
        # depth_image_normalized = (depth_image - np.min(depth_image)) / (np.max(depth_image) - np.min(depth_image))

        cv2.imshow("depth", depth_colormap)
        cv2.setMouseCallback("depth", mouse_move,1) 
        key = cv2.waitKey(1)
        import datetime
        
        if key == ord("e"):
            import os
            now = datetime.datetime.now()
            fname = now.strftime('%Y-%m-%d %H:%M:%S').replace(":",".")
            os.mkdir("data/"+fname)
            x=rs.save_single_frameset("data/"+fname+"/data_frame")
            x.process(frames)
            cv2.imwrite("data/"+fname+"/depth_image.png", depth_image)
            cv2.imwrite("data/"+fname+"/RGB_image.png", color_image)
            cv2.imwrite("data/"+fname+"/IR1_frame.png", IR_frame)
            cv2.imwrite("data/"+fname+"/IR2_frame.png", IR1_frame)
            cv2.imwrite("data/"+fname+"/colored_depth.png", depth_colormap)
            cv2.imwrite("data/"+fname+"/normalized_depth.png", depth_image_8bit)

            # cv2.imwrite("data/"+fname+"/distance.pfm", distance_pfm)
            save_pfm("data/"+fname+"/distance.pfm",distance_pfm)
            # cv2.imwrite("data/"+fname+"/wls_filtered_depth.png", coloredDisp)


            ply = rs.save_to_ply("data/"+fname+"/point_cloud_bin.ply")

            # Set options to the desired values
            # In this example we'll generate a textual PLY with normals (mesh is already created by default)
            ply.set_option(rs.save_to_ply.option_ply_binary, True)
            ply.set_option(rs.save_to_ply.option_ply_normals, False)

            print("Saving to 1.ply...")
            # Apply the processing block to the frameset which contains the depth frame and the texture
            ply.process(filtered_frame)

            ply2 = rs.save_to_ply("data/"+fname+"/point_cloud_text.ply")
            ply2.set_option(rs.save_to_ply.option_ply_binary, False)
            ply2.set_option(rs.save_to_ply.option_ply_normals, True)
            ply2.process(filtered_frame)

        #print("Done")
finally:
    pipeline.stop()
