
# AMR FINAL PROJECT


## Important Information

| Item | Details |
|------|---------|
| Assignment Release | 1 July 2026 |
| Due Date | **28 September 2026, 23:59 CET** |
| Repository Visibility | Public |
| Team Size | 3–4 students |
| Submission | Prepare a report with the format explained in class and Submit the GitHub repository URL on LEA |

# AMR Project

## Project Objectives

The objective of this project is that you deploy some of the functionalities that were discussed during the course on a real robot platform. In particular, we want to have functionalities for path and motion planning, localisation, and environment exploration on the robot.

We will particularly use the Robile platform during the project; you are already familiar with this robot from the simulation you have been using throughout the semester as well as from the few practical lab sessions that we have had.

## Task Description

The project consists of three parts that are building on each other: (i) path and motion planning, (ii) localisation, and (iii) environment exploration.

## 1. Path and Motion Planning

You have already implemented a *potential field planner* in one of your assignments. In this first part of the project, you need to port your implementation to the real robot and ensure that it is working as well as it was in the simulated environment so that you can navigate towards global goals while avoiding obstacles. Then, integrate your potential field planner with a global path planner, namely first use a path planner (e.g. A*) to find a rough global trajectory of waypoints that the robot can follow to reach a goal and then use the potential field planner to navigate between the waypoints. This will make your potential field planner applicable to large environments, where it can navigate given an environment map.

The following steps start the path and motion planning:

### 1) Build the workspace

Build the workspace:

```bash
colcon build
```

Source ROS 2 Humble and the workspace:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

### 2) Start the Gazebo Simulation

Open a new terminal, source the workspace, and run:

```bash
ros2 launch robile_gazebo gazebo_4_wheel.launch.py
```

### 3) Start the Map Server

Start the Nav2 map server and provide the map YAML file:

```bash
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:="$(pwd)/my_map.yaml"
```

### 4) Activate the Map Server

Open a separate terminal and configure and activate the map server:

```bash
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

The map should now be available over the `/map` topic and can be visualized in RViz.

### 5) Start the Wavefront Planner

Open a new terminal and run:

```bash
ros2 run wavefront wave
```

The Wavefront planner uses the occupancy grid to compute a global path from the robot's current position to the selected goal.

### 6) Select the Goal in RViz

In RViz, use the **Publish Point** tool to select the desired goal position on the map.

The selected point is published over the following topic:

```text
/clicked_point
```

The Wavefront planner receives the selected goal and computes a path towards it.

Once the path has been generated, it is published over:

```text
/wavefront_path
```

### 7) Start the Potential Field Planner

Open another terminal and run:

```bash
ros2 run potential potential
```

## 2. Localisation

In one of the course lectures, we discussed Monte Carlo localisation as a practical solution to the robot localisation problem in an existing map. In this second part of the project, your objective is to implement your very own particle filter that you then integrate on the Robile. You should implement the simple version of the filter that we discussed in the lecture; however, if you have time and interest, you are free to additionally explore extensions / improvements to the algorithm, for example in the form of the adaptive Monte Carlo approach that we mentioned in the lecture.


# MCL Particle Filter – Robile Simulation

This project implements a simple **Monte Carlo Localisation (MCL) particle filter** for the Robile mobile robot.

The localisation system is tested in **Gazebo simulation** using a known map, robot odometry, and front LiDAR data. RViz2 is used to visualise the map, robot, LiDAR, TF frames, and particle distribution.

## Requirements

- ROS 2 Humble
- Gazebo
- Robile ROS 2 packages
- Nav2 Map Server
- RViz2
- `teleop_twist_keyboard`

## Running the Simulation

The following steps should be run in separate terminals.

### 1. Start Gazebo

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch robile_gazebo gazebo_4_wheel.launch.py
```

Keep this terminal running.

### 2. Start the Map Server

Open a new terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_map_server map_server \
  --ros-args \
  -p yaml_filename:=/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/robile_navigation/maps/closed_walls_map.yaml \
  -p use_sim_time:=true
```

The map is defined by `closed_walls_map.yaml` and its corresponding PGM file.

### 3. Configure and Activate the Map Server

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 lifecycle get /map_server
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
ros2 topic echo /map --once | head -25
ros2 lifecycle get /map_server
```

The Map Server should be active before continuing.

### 4. Start the MCL Particle Filter

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run amr_localization lo --ros-args -p use_sim_time:=true
```

The filter uses `/map`, `/odom`, and `/scan` and publishes the particle-filter localisation results.

### 5. Start RViz2 / Navigation Visualisation

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch robile_navigation online_async.launch.py
```

RViz2 can be used to observe the map, robot, LiDAR scans, TF frames, particle cloud, and estimated pose.

### 6. Move the Robot

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use the keyboard to move the Robile around the simulated environment. The MCL particle filter updates the particle distribution using odometry and LiDAR measurements.


# Running on robile



The following steps should be run in separate terminals.

### 0. Set Up Each Terminal

Before running the commands in each terminal, go to the project directory, source ROS 2 and the workspace, and set the ROS domain ID.

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1
```

The `ROS_DOMAIN_ID` depends on the Robile being used. Use the appropriate value:

```text
ROS_DOMAIN_ID=1
ROS_DOMAIN_ID=2
ROS_DOMAIN_ID=3
ROS_DOMAIN_ID=4
```

For the simulation, use the domain ID configured for your setup.

### 1. Start Gazebo

Open a new terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1

ros2 launch robile_gazebo gazebo_4_wheel.launch.py
```

Keep this terminal running.

### 2. Load the Map

Open a new terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1

ros2 run nav2_map_server map_server \
  --ros-args \
  -p yaml_filename:=/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/robile_navigation/maps/lab_map_updated.yaml \
  -p use_sim_time:=false
```

The YAML file loads the corresponding PGM occupancy-grid map.

### 3. Configure and Activate the Map Server

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1

ros2 lifecycle get /map_server
```

Configure the map server:

```bash
ros2 lifecycle set /map_server configure
```

Activate it:

```bash
ros2 lifecycle set /map_server activate
```

Check that the map is being published:

```bash
ros2 topic echo /map --once | head -25
```

Check the lifecycle state again:

```bash
ros2 lifecycle get /map_server
```

### 4. Start the MCL Particle Filter

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1

ros2 run amr_localization particle_filter_localization \
  --ros-args \
  -p use_sim_time:=false
```

The particle filter uses the map, robot odometry, and LiDAR measurements to estimate the robot pose.

### 5. Start RViz2

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1

rviz2
```

RViz2 can be used to observe the map, robot, LiDAR scans, TF frames, particle cloud, and estimated pose.

### 6. Move the Robot

Open another terminal:

```bash
cd ~/HBRS/AMR/AMR_PROJECT/amr-team-bot
source /opt/ros/humble/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=1

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use the keyboard to move the Robile around the simulated environment. The MCL particle filter updates the particle distribution using odometry and LiDAR measurements.









## 3. Environment Exploration

The final objective of the project is to incorporate an environment exploration functionality to the robot. This will have to be combined with a SLAM component, namely you will need your exploration component to select poses to explore and a SLAM component that will take care of actually creating a map. The exploration algorithm should ideally select poses at the map fringe (i.e. poses that are at the boundary between the explored and unexplored region), but you are free to explore different pose selection strategies in your implementation.

The following steps start the exploration:

### 1) Build the workspace

Navigate to the exploration workspace and build it:

```bash
colcon build
```

Source ROS 2 Humble and the workspace:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

### 2) Start the Gazebo Simulation

Open a new terminal, source the workspace, and run:

```bash
ros2 launch robile_gazebo gazebo_4_wheel.launch.py gui:=false
```

### 3) Start SLAM Toolbox

Open a new terminal, source the workspace, and run:

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```
### 4) Start Nav2

Open a new terminal, source the workspace, and run:

```bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true
```

### 5) Start the Robile Bringup

Open a new terminal, source the workspace, and run:

```bash
ros2 launch robile_bringup robot.launch.py
```

### 6) Start the Exploration Node

Finally, open another terminal, source the workspace, and start the exploration node:

```bash
ros2 run my_explorer explorer_exe
```
