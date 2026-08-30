
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