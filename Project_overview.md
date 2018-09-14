## Project #1: Search and Sample Return
Project submission for the Udacity Robotics Software Engineer Nanodegree by **Rohit Kumar Mishra

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  


## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  



### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

My version of the Jupyter Notebook can be found here <a href="https://github.com/rohit0453/Udacity-RoboND-Project-1-search-and-sample-return/blob/master/RoboND-Rover-Project-master-RohitKumarMishra/code/Rover_Project_Test_Notebook_Rohit_Kumar_Mishra.ipynb">Link</a>



#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
The process_image() function has been updated to draw the worldmap using the test dataset obtained from Udacity RoverSim. 

Here is the video
<a href="https://github.com/rohit0453/Udacity-RoboND-Project-1-search-and-sample-return/blob/master/RoboND-Rover-Project-master-RohitKumarMishra/output/test_mapping_Rohit.mp4" >Link</a>
### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

I have modified the `rock_finder()` function. Single threshold do not recognise the rock ,when placed near to the mountains. So, I defined 2 tuples as lower and upper threshold tuples.

```python
def rock_finder(img, thresh_low=(130, 111, 0), thresh_high=(211, 170, 40))
```

As per **Optimizing Map Fidelity Tip** to select the images nears roll and pitch is zero.

```python
true_img = True

if Rover.pitch > 0.25 and Rover.pitch < 359.75:
        true_img = False
    elif Rover.roll > 0.75 and Rover.roll < 359.25:
        true_img = False
```
#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  
I have operated the RoverSim in 640x480 resolution. The Rover were able to autonomously drive around mapped over 40% and with more than 60% of fidelity and
was able to collect 2 rock samples.

Here is the link to youtube video :

<a href="https://www.youtube.com/watch?v=xkWSE77J100">Youtube link</a>

#### How it could be given a brain to not to revisit the same place.
Using dynamic programming memoization technique, we can record the Rover position and a patch of neighbouring pixel around it and append those values to some collection data type variable. Now conditions can be applied using `if else`If those values already exist in collection then stear your rover.


I was able to meet the passing requirements (60% fidelity and 40% mapped and atleast collecting one rock sample) for the Rover's project.

