# Blender Triangulate Addon

Files:
triangulate.py - the addon


TriangulateTestBlend.zip - contains two short video files and a blend file showing the naming schemes described below


## Introduction

Optical MoCap systems use two or more calibrated cameras to track markers on a mocap actor or prop. The tracking data, and the known location of the cameras allows software to determine the 3D location of each marker by triangulation.

Blender's tracking abilities have improved so much recently that it seems that it's standard functionality can be used to do most of the calibration and tracking functions required for a mocap session. This 'Triangulate' addon has been created to do the final piece of the puzzle. Before running the addon, it's necessary to have set up two or more movie clips with tracking data for the markers on a mocap actor. There must also be matching 3d cameras in a 3d scene which accurately match the location, rotation and lens/sensor data of the real cameras which produced the movieclip footage. 

The 'triangulate' addon will combine the movieclip tracking data with the 3d camera locations, and will add keyframes to a series of empties to make them match the 3d position of the actor's tracking markers.

The Empties can then be used by the 3d artist to drive an armature, or any other purpose. The built-in 'Motion Capture' addon can also be used to retarget the captured actions to a target armature or rig.


## Installation
The 'triangulate addon is installed using the standard blender method. From the Addon tab on User Preferences dialog, choose 'Install from file'. Navigate to the 'Triangulate.py' file, and select it. You can then enable the addon via the check box.

## Pre-work
The 'triangulate' addon is just one small part of a larger workflow. This section lists some of the other tasks required to do motion capture. There may be many ways to achieve the same outcome.

- Choose two or more cameras to film the mocap actor. They should be able to film at the same framerate, but can be different in most other ways. 
- Determine the actual lens focal length and crop factor. There are lots of ways of doing this, and most tutorials on motion tracking in blender will at least mention this.
- Optionally film calibration markers, and then film the actions of a mocap actor (preferably wearing tracking markers of some kind) with two or more cameras. Note the camera must have the same framerate. The cameras should be placed so that they view the scene from a significantly different angle
- Edit the two or more video files to be time synchronized. (And probably to contain only the relevant parts of calibration and actions)
- Load the two or more video files into 'Movieclips' in Blender. Give each one a distictive name (eg Camera1)
- Create a matching camera in 3D space for each Movieclip. Each camera must have exactly the same location, rotation, and sensor and lens settings as the real cameras used to produce the Movieclip video. This is the hard part, and the triangulate addon doesn't help with this! See the later section on Camera Calibration for some suggestions on how to do this.
- Name each 3D camera object exactly the same as it's matching Movieclip. For example, if the first MovieClip is named "Camera1", then the matching 3D camera object name should be "Camera1". If the Movieclip name is "Camera1.MOV", then the camera name should be "Camera1.MOV".
- For each Movieclip, use Blender's impressive tracking features to track each Mocap marker for the duration of the action being recorded. Each track should be given a distinct name. For example, the marker on the actor's left knee could be called "Knee.L". Make sure that the same track name is given in each Movieclip for each track on the same physical marker. For example, if "Knee.L" is used for the track name for the marker on the left knee on Camera1, then "Knee.L" must be the name given to the track on Camera2 for that same marker. Note that it doesn't matter which Movieclip object the track is attached to - it can be the default camera object or you can add an object like 'Actor'.
Note that we are just doing 2D tracking for the 'Triangulate' addon, no camera solve is required (unless you use this for camera calibration - see the later section)
- For each track name created in the two or more Movieclips, create an Empty in the 3D viewport with the same name. For example, if you called the actor's left knee "Knee.L" in movieclips "Camera1" and "Camera2", then you need to create an empty called "Knee.L". This tells the 'triangulate' addon to look for tracks called "Knee.L" in every Movieclip in the project, and if it finds this track in at least to Movieclips, it will add location keyframes to the empty.

## Running the Addon
Finally, the hard work is done! Set the start and end frames to the range that you want the empties animated.

Go to the 3D view, and press the 'Triangulate' button on the "Misc" toolshelf tab, (or in the Object Menu). For every empty in the scene, and for every the frame from 'start' to 'end', the addon will look for tracks with matching names in each Movieclip. If it finds tracks with valid tracking information in at least two Movieclips, it will perform a triagulation calculation to determine the 3D location of the tracked marker, and will add a location keyframe to the empty. This should happen very quickly.

If you scrub through the frames in the scene, the empties should move with the same motion as the Mocap actor.

There should be two values in the Triangulate section of the Redo panel, labelled "Max Error", and "Average Error".

If the camera calibration is perfect, the rays that are projected through the tracking points should meet exactly, and that is the point used for the keyframe. However, that's unlikely! The rays will probably miss each other by some distance. This distance is used as the error value, and the point chosen for the keyframe is the mid point of the closest distance between the rays. The "Average Error" is the average distance in blender units of all the keyframes. The "Max Error" pararmeter allows you to select the maximum error for which a keyframe is created. This give the possibility of removing outliers automatically.

For each empty, a custom parameter called 'Error" is added, and a keyframe is added for every frame showing the error for that frame. You can use the graph function to trend this error for each empty, and perhaps manually delete bad keyframes.

## Using the Empties
Moving empties aren't that useful in themselves, but the idea is that you should create an armature which matches the dimensions of the mocap actor, and give the joints constraints to limit motion to feasible movements. One empty (for example the "hip" empty), or perhaps a group of three empties can determine the base location of the root or 'hip' bone using a location constraint, and the other empties can be used to target rotations is the other bones.

If the bone constraints are converted to keyframes, the it should be possible to use the built in "Motion Capture" addon to clean up and retarget the motion data to the final rig.

Or you can do whatever you like with them!!


## Camera Calibration

Accurate camera calibration is the biggest issue in this Mocap method. It's up to you how to do this for your application, but here are two suggestions...

Method 1 - Camera tracking
This was my original plan. I added at least 8 tracking markers to a real 3D object (a chair in my case). Before filming the Mocap actions, I had both cameras (could be more than two) film the chair being moved smoothly on at least two axies.
When the Movieclips were imported to Blender, I used the camera tracking functions to solve the camera motion, pretending the chair (or calibration object) was still, and both cameras were moving around. Of course I had to add the camera lens and sensor data to the movieclips before solving. One movieclip at a time, I created a tracking scene and used the 'distance' scaling function on two markers to set the scene size to the real world scale, and then set the origin to one marker, the Y axis to another marker, and the X axis to a third marker. 

This created a camera with the correct lens and sensor values, with approximately the correct location and rotation relative to the calibration object. I renamed the camera the same as the Movieclip, and I converted to camera tracking constraint to keyframes. I then deleted all the keyframes except for one which matched with the chair (calibration object) sitting still one the ground. I also named the action in the action editor and hit the 'F' button as the camera can be deleted when the next tracking scene is created, and this lets you get back the position easily.

I repeated this for the other Movieclip. It's obviously important to use the same markers for these various scaling and axis functions so that the second camera has the correct relationship to the calibration object.

This method worked but only seems accurate when the mocap actor was in the same region as the calibration object. A lot depends on the quality of the tracking and the movement of the object. It was also a fair bit of work for each camera, and would have to be repeated each time the cameras were moved.

** Edit - this method is crap **

Method 2
** Edit - this method is pretty good **

I plan to model the physical characteristics of the Mocap set to scale in 3D. I will then measure the actual position of the cameras in the set. I will also check that the camera's tripods are level.

Then I will manually place the virtual cameras in the 3D scene. The only parameters that should need to be adjusted are the pan and tilt of the cameras, and I'll line up the actual video of the Mocap stage with the 3D model of the stage.

Camera Focal Length Detection
I've tried a few different ways to determine the focal length of the cameras I use. (Not just for this project - it's useful in all camera tracking applications).

The best method I've found so far is to use the free panorama creation program 'Hugin'. There is lots of information on the net on how to use this. I then find a location where I can see two points some distance away which I know are 90 degrees from each other (eg a street corner). Using the camera's video mode (the video mode can have a very different focal length than the stills mode as the whole sensor may not be used), I try to get two or three fairly steady frames of the two distant points and as many intermediate frames as required to get an overlap.

I then use blender or an external editor to extract those two or three frames to jpeg files, and use Hugin to produce a panorama, guessing the focal lenth and crop factor. You can set the preview to be equirectangular with a horizontal 
angle of 90 degrees. If you guess correctly, the two distant points should be at the edges of the preview. Otherwise adjust your guess and try again.

This method seems quite accurate. If you want to be even more accurate, do a full 360 deg panorama. Hugin can work out the exact focal length in order for the images to make a full circle. It will also work our the barrel distortion accurately, but I haven't worked if the numbers produce match Blender's method.





