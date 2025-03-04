#importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import datetime
import math
import os
from collections import deque


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(graye)"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)

def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def region_of_interest(img, vertices):
    """
    Applies an image mask.

    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    #defining a blank mask to start with
    mask = np.zeros_like(img)

    #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    #filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).

    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.

    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)



def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    draw_lines(line_img, lines, thickness= 5)
    return  lines, line_img

# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, α=0.8, β=1., γ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.

    `initial_img` should be the image before any processing.

    The result image is computed as follows:

    initial_img * α + img * β + γ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, γ)

def show_images(images, image_name= '',cmap= None):
    SAVE_DIR = 'test_images_output/'
    directory = ''
    cols = 2
    rows = (len(images)+1)//cols

    plt.figure(figsize=(10, 11))
    for i, image in enumerate(images):
        plt.subplot(rows, cols, i+1)
        # use gray scale color map if there is only one channel
        cmap = 'gray' if len(image.shape)==2 else cmap
        plt.imshow(image, cmap=cmap)
        plt.xticks([])
        plt.yticks([])
    plt.tight_layout(pad=0, h_pad=0, w_pad=0)
    if os.path.isdir(SAVE_DIR):
        directory = SAVE_DIR
    image_name = str(datetime.datetime.now()).split('.')[0].replace(' ', '').replace(':','').replace('-', '') if image_name == '' else image_name
    plt.savefig(directory + image_name + '.png', bbox_inches = 'tight')
    plt.show()

def select_white_yellow_colors(image):
    # White color mask

    lower_white = np.uint8([200, 200, 200])
    upper_white = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(image, lower_white, upper_white)

    # Yellow color mask

    lower_yellow = np.uint8([190, 190,   0])
    upper_yellow = np.uint8([255, 255, 255])
    yellow_mask = cv2.inRange(image, lower_yellow, upper_yellow)

    # One mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    masked_image = cv2.bitwise_and(image, image, mask = mask)
    return masked_image

def convert_to_hsl(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)

def select_white_yellow_colors_HSL(image):

    # Convert the image to HSL
    hsl_image = convert_to_hsl(image)
    # White color mask

    lower_white = np.uint8([0, 200, 0])
    upper_white = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(hsl_image, lower_white, upper_white)

    # Yellow color mask

    lower_yellow = np.uint8([10, 0, 100])
    upper_yellow = np.uint8([40, 255, 255])
    yellow_mask = cv2.inRange(hsl_image, lower_yellow, upper_yellow)

    # One mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    masked_image = cv2.bitwise_and(image, image, mask = mask)
    return masked_image

def canny_edges(image, low_threshold = 50, high_threshold = 150):
    return canny(image, low_threshold, high_threshold)

def apply_region_of_interest(image):
    # four sided polygon as a mask
    imshape = image.shape
    xsize = imshape[1]
    ysize = imshape[0]
    # Top-Left, Top-right, Bottom-right, Bottom-left
    vertices = np.array([[(xsize * 0.05, ysize) # Bottom left
                     , (xsize * 0.45, ysize * 0.60)  # Top left vertix 60% if the image's hight
                     , (xsize * 0.55, ysize * 0.60) # Top right vetrix
                     , (xsize * 0.95, ysize)]] # Bottom right
                        , dtype=np.int32)
    return region_of_interest(image, vertices)

def hough_transform(image):
    # Apply Hough transform on the Canny edged image
    rho = 1 # distance resolution in pixels of the Hough grid
    theta = 1 * (np.pi/180) # angular resolution in radians of the Hough grid
    threshold = 20     # minimum number of votes (intersections in Hough grid cell)
    min_line_len = 20 #minimum number of pixels making up a line
    max_line_gap = 200    # maximum gap in pixels between connectable line segments

    return hough_lines(image, rho, theta, threshold, min_line_len, max_line_gap)

def average_slope_yintercept(lines):
    left_lane_lines = []
    left_lane_weights = []
    right_lane_lines = []
    right_lane_weights = []

    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = (y2 - y1) / (x2 - x1)
            y_intercept = y1 - slope * x1

            # Right lane line
            line_length = np.sqrt((y2-y1)**2 + (x2-x1)**2 )
            if slope > 0:
                right_lane_lines.append((slope, y_intercept))
                right_lane_weights.append((line_length))
            # Left lane line
            else:
                left_lane_lines.append((slope, y_intercept))
                left_lane_weights.append((line_length))

    # Weight slopes and Y_intercepts by their line lenght
    right_lane = np.dot(right_lane_weights, right_lane_lines) / np.sum(right_lane_weights) if len(right_lane_weights) > 0 else None
    left_lane  = np.dot(left_lane_weights,  left_lane_lines) / np.sum(left_lane_weights)  if len(left_lane_weights) > 0 else None

    return right_lane, left_lane

def make_points(y1, y2, line):
    if line is None:
        return None

    slope, intercept = line

    x1 = int((y1 - intercept)/slope)
    y1 = int(y1)
    x2 = int((y2 - intercept)/slope)
    y2 = int(y2)

    return ((x1, y1), (x2, y2))

def make_lane_lines(image, lines):
    right_lane, left_lane = average_slope_yintercept(lines)#seperate_lanelines(lines)

    y1 = image.shape[0] # Y value Opencv has everything inverted
    y2 = y1 * 0.60

    right_line = make_points(y1, y2, right_lane)
    left_line  = make_points(y1, y2, left_lane)

    return right_line, left_line

def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=2):
    line_img = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
    for line in lines:
        if line:
            cv2.line(line_img, *line, color, thickness)
    return weighted_img(image, line_img)

from collections import deque
class LaneLineFinder:

    SAMPLE_FRAMES = 30

    def __init__(self):
        self.right_lane_lines = deque(maxlen= self.SAMPLE_FRAMES)
        self.left_lane_lines = deque(maxlen= self.SAMPLE_FRAMES)

    def average_line_sampling(self, line, previous_lines):
        if line:
            previous_lines.append(line)

        if len(previous_lines) > 0:
            line = np.mean(previous_lines, axis = 0, dtype=np.int32) # Like tensorflow
            line = tuple(map(tuple, line))

        return line

    def process_image(self, image):
        # NOTE: The output you return should be a color image (3 channel) for processing video below
        # TODO: put your pipeline here,
        # you should return the final output (image where lines are drawn on lanes)

        # Convert image to the HSL color space
        white_yellow_image = select_white_yellow_colors_HSL(image)
        # grayscaling the image
        gray_image = grayscale(white_yellow_image)

        # then we apply Gaussian Blur to denoice the Gray image before getting canny edges
        # Denoise image using Gaussian Blur
        denoised_image = gaussian_blur(gray_image, 11)

        # then we apply canny edges to detect the image edges
        canny_image = canny_edges(denoised_image)


        # Apply region of intrest mask on the canny edges image
        masked_image = apply_region_of_interest(canny_image)


        # Apply Hough transform on the Canny edged image
        # Applying Hough transform and drawing the lines on the image
        image_lines = hough_transform(masked_image)

        # Extrapolate lanelines return by the Hough transform
        extrapolated_lane_lines = make_lane_lines(image, image_lines[0])


        # Average the videos last 6 lines' frames
        right_line = self.average_line_sampling(extrapolated_lane_lines[0], self.right_lane_lines)
        left_line = self.average_line_sampling(extrapolated_lane_lines[1], self.left_lane_lines)

        # Draw laneLines on the mage with lane lines colored
    #     image_copy = np.copy(image)

        return draw_lane_lines(image, (right_line, left_line), thickness= 18)
