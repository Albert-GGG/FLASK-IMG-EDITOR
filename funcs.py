import cv2
import numpy as np

# Change image to gray scale
def Grays(in_image):
    gray_scale = cv2.cvtColor(in_image, cv2.COLOR_RGB2GRAY)
    return gray_scale

# Obtain contours of image and inverts colors
def Contours(in_image, is_inverted):
    canny = cv2.Canny(in_image, 50, 200)
    if is_inverted:
        return cv2.bitwise_not(canny)
    
    return canny

# Blurs the image indicating size of kernel
def Blurring(in_image, k):
    if k <= 0:
        return in_image
    blur = cv2.blur(in_image, (k,k))
    return blur
    
# Modify brightness of image
def Brightness(in_image, value):
    
    # Create a kernel with values to add or substract from the image
    mat = np.ones(in_image.shape, dtype = 'uint8') * abs(value)  
    if value >= 0:                  
        imgBrillo = cv2.add(in_image, mat)
    else:                           
        imgBrillo = cv2.subtract(in_image, mat)

    return imgBrillo

# Apply a theshold filter to the image
def Threshold(in_image, low_bound, up_bound):
    ret, bw = cv2.threshold(Grays(in_image), low_bound, up_bound, cv2.THRESH_BINARY)
    return bw

# Split the image in different regions according to a specified number of rows and columns
def Split(in_image, rows, columns):

    height_region, width_region = int(in_image.shape[0] / rows), int(in_image.shape[1] / columns)
    regions = list()

    for rs in range(rows):
        for cs in range(columns):
            new_region = in_image[rs * height_region:height_region * (rs + 1), cs * width_region:width_region * (cs + 1)]
            regions.append(new_region)

    return regions

# Split image and return regions in a list o of lists representing the rows and columns
def SplitStripes(in_image, rows, columns):

    height_region, width_region = int(in_image.shape[0] / rows), int(in_image.shape[1] / columns)
    regions = []

    for rs in range(rows):
        h_regions = list()
        for cs in range(columns):
            new_region = in_image[rs * height_region:height_region * (rs + 1), cs * width_region:width_region * (cs + 1)]
            h_regions.append(new_region)
        regions.append(h_regions)

    return regions

def mergeImg(regions):
    reg_height = regions[0][0].shape[0]
    white = [255, 255, 255]
    
    hor_list = list()
    whiteH = np.zeros((reg_height, 10, 3), dtype=np.uint8)
    whiteH[:] = white
    
    # Add white border to the right of images
    for row in range(len(regions)):
        for reg in range((len(regions[row]) - 1)):
            regions[row][reg] = np.concatenate((regions[row][reg], whiteH), axis=1)
    
    # Merge columns of each row
    for row in regions:
        hor_list.append(np.concatenate(([f for f in row]), axis=1))

    reg_width = hor_list[0].shape[1]
    whiteW = np.zeros((10, reg_width, 3), dtype=np.uint8)
    whiteW[:] = white

    for merged_row in range(len(hor_list) - 1):
        hor_list[merged_row] = np.concatenate((hor_list[merged_row], whiteW), axis=0)

    merged_img = np.concatenate(([reg for reg in hor_list]), axis=0)

    return merged_img