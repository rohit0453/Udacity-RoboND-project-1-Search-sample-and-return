import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select
def rock_finder(img, thresh_low=(130, 111, 0), thresh_high=(211, 170, 40)):

    colorsel = np.zeros_like(img[:,:,0])

    within_thresh = (img[:,:,0] > thresh_low[0]) & (img[:,:,1] > thresh_low[1]) & (img[:,:,2] > thresh_low[2]) & (img[:,:,0] < thresh_high[0]) & (img[:,:,1] < thresh_high[1]) & (img[:,:,2] < thresh_high[2])
    
    colorsel[within_thresh] = 1
    return colorsel
# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image

    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    
    return warped, mask


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    image = Rover.img

    true_img = True
    # 0) Image is really only valid if roll and pitch are ~0
    if Rover.pitch > 0.25 and Rover.pitch < 359.75:
        true_img = False
    elif Rover.roll > 0.75 and Rover.roll < 359.25:
        true_img = False
    
    # 1) Define source and destination points for perspective transform
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    dst_size = 5
    bottom_offset =6
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])
    # 2) Apply perspective transform
    warped , mask = perspect_transform(image,source,destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    terrain = color_thresh(warped)
    obstacle = np.absolute(np.float32(terrain-1))*mask
    rock_sample = rock_finder(warped)
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,0] = obstacle*255
    Rover.vision_image[:,:,1] = rock_sample*255
    Rover.vision_image[:,:,2] = terrain*255

    # 5) Convert map image pixel values to rover-centric coords
    nav_xpix,nav_ypix = rover_coords(terrain)
    obs_xpix,obs_ypix = rover_coords(obstacle)
    rock_xpix,rock_ypix = rover_coords(rock_sample)
    # 6) Convert rover-centric pixel values to world coordinates
    scale = 10
    navigable_x_world,navigable_y_world = pix_to_world(nav_xpix,nav_ypix,Rover.pos[0],Rover.pos[1],Rover.yaw,Rover.worldmap.shape[0],scale)
    obstacle_x_world,obstacle_y_world = pix_to_world(obs_xpix,obs_ypix,Rover.pos[0],Rover.pos[1],Rover.yaw,Rover.worldmap.shape[0],scale)
    rock_x_world,rock_y_world = pix_to_world(rock_xpix,rock_ypix,Rover.pos[0],Rover.pos[1],Rover.yaw,Rover.worldmap.shape[0],scale)

    if rock_sample.any():

        rock_distance, rock_angle = to_polar_coords(rock_xpix, rock_ypix)
        rock_index = np.argmin(rock_distance)
        rock_x_center = rock_x_world[rock_index]
        rock_y_center = rock_y_world[rock_index]
        Rover.rock_angle = rock_angle
        Rover.rock_dist = rock_distance
    else:
        Rover.rock_angle = None
        Rover.rock_dist = None
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    # only update world mape if camera image was valid
    if true_img:
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 5

        if rock_sample.any():
            Rover.worldmap[rock_y_center, rock_x_center, 1] += 245

        Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 40
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    rover_centric_pixel_distances, rover_centric_angles = to_polar_coords(nav_xpix, nav_ypix)
    Rover.nav_angles = rover_centric_angles
    Rover.nav_dists = rover_centric_pixel_distances
 
    
    
    return Rover