# Helena-Repository
Welcome to My GitHub Repository!

👋 Hi! I’m Helena Sieh, a Robotics Engineering student at the University of Michigan.
This repository showcases selected research and coursework in robotics, perception, and AI, including projects using NVIDIA Jetson Orin, Isaac Sim, ROS2, and machine learning.

## Table of Contents
- [Tour Guide Robot (MAVRIC Lab)](#tour-guide-robot-may-2025---present)
- [Human Visual Perspective Taking Estimation](#human-visual-perspective-taking-estimation-aug-2024---may-2025)
- [Course Projects](#course-projects)
  - [ROB 102: Intro to AI and Programming](#rob-102-fall-2024)
  - [ENGR 100: Robotics & Mechanisms](#engr-100-fall-2024)
  - [EECS 280: Programming and Data Structures](#eecs-280-fall-2025)
- [Independent Projects](#independent-projects)


### 🚀 [TOUR GUIDE ROBOT]  
**Role:** Undergraduate Researcher, MAVRIC Lab ([MAVRIC]([url](https://mavric.si.umich.edu/home))), University of Michigan  
**Timeline:** May 2025 – Present  

**Overview:**  
Investigating how mixed-agent (robot + virtual avatar) tour guide systems influence user satisfaction and learning performance. Designed a new behavioral metric, Following, based on observable human gaze, proximity, and movement data to improve real-world human–robot interaction.

**Key Contributions:**  
- Collaborated on the development of a tour guide robot system to measure human-robot following behaviors.
- Built real-time software modules in ROS Noetic for multi-sensor data fusion on the Toyota Human Support Robot (HSR).
- Implemented multi-camera ArUco marker detection in Python for precise human localization.
- Engineered and optimized PID control loops for dynamic robot head orientation, maintaining continuous engagement.
- Integrated an additional Intel RealSense D435i to enhance perception and environmental awareness.
- Designed flexible user study environments, iterating based on empirical behavioral data. 

**Technologies:** ROS/ROS2, Python, ArUco, PID Control, Intel RealSense D435i, Toyota HSR, SLAM, Human–Robot Interaction  

**Demo:** 

[Watch a short demo video here](https://drive.google.com/file/d/1RP4j1KjlgW5vL6yS8Cnq2BmeUxjTizo1/view?usp=sharing)

Below are some images of my contributions:<br>

Robot projecting virtual avatar during tour session:<br>
<img width="509" height="662" alt="Screenshot 2025-08-22 at 4 40 08 PM" src="https://github.com/user-attachments/assets/59caac8c-e485-4115-b980-16ed2094ae46" />

Point Cloud Reconstruction in Open3D:<br>
<img width="578" height="318" alt="Screenshot 2025-08-22 at 4 44 00 PM" src="https://github.com/user-attachments/assets/909f2355-df14-47c3-bfff-a68b929edc6d" />


# HUMAN VISUAL PERSPECTIVE TAKING ESTIMATION (August 2024 - May 2025)
Undergraduate Reasearcher at the University of Michigan Autonomous Vehicle Research Intergroup Collaboration ([MAVRIC]([url](https://mavric.si.umich.edu/home))) Lab:**
https://sites.google.com/view/umich-urop2024-25-engagement/setting-nvida-isaac

This project explores the question: How can robots estimate human visual perspective (VPT) using only common onboard sensors?
  
- Visual Perspective Taking (VPT) is the ability to understand another person’s viewpoint, taking into account what they see and how they see it.
- Developed a novel multi-modal VPT extraction algorithm that integrates:
  - Visual SLAM (VSLAM) to build a 3D map of the environment
  - RGB-D sensor data to track human head and gaze positions in real-time
  
  Features
  - Real-time human head and gaze tracking
  - Integration with RGB-D cameras (e.g. Intel RealSense)
  - SLAM-based scene reconstruction using RTAB-Map
  - ROS-compatible architecture
  - Open3D-based rendering and visual output
  - Output visualization in RViz and ROS image topics

<img width="684" alt="Screenshot 2025-06-08 at 2 02 51 PM" src="https://github.com/user-attachments/assets/9fc4ad04-928c-46e5-a01a-88d8830fc96f" />


# ROB 102 (Fall 2024): Introduction to AI and Programming:
Below are some of the projects that I worked on in this class. These projects range from driving in a star to wall following to developing a breadth first search path planning algorithm.

**Project 1 Wall Follower Checkpoint Videos**
- [Drive Square Demo](https://drive.google.com/file/d/1tMW7yRODxny66sLa-o42Muot1w4mKYjA/view?usp=sharing)
- [Follow Me 1D Demo](https://drive.google.com/file/d/1LWufWUzry9QBVPiw17irv8JxUTdeV4BC/view?usp=sharing)
- [Drive Star Demo](https://drive.google.com/file/d/1qEvuWSZ3VkWlhqoXxU7Be2pLKbptl9lT/view?usp=sharing)
- [Follow Me 2D Demo](https://drive.google.com/file/d/1-6NgjZ3PY8BDyGQ-sMeC_WCJ1zHDHbSd/view?usp=drive_link)
- [Wall Follower Demo](https://drive.google.com/file/d/1SdfmCH3lXhFtj_JmQFho2R_S6ZB3bOaO/view?usp=sharing)

**Project 2 Bug Navigation Checkpoint Videos**
- [Robot Hits the Spot Demo](https://drive.google.com/file/d/1KOR-LOGgDojt7m0uWE1eUbCL8nmE_8x8/view?usp=sharing)
- [Bug Navigation Demo](https://drive.google.com/file/d/1i5BkDj3tiplTPPgzpDKMhSkoJJNv6JMl/view?usp=sharing)

# ENGR 100 (Fall 2024): Robotics & Mechanisms:
Built a fully autonomous mBot-based system that detects ice using thermal sensors, and deploys salt through a closed-loop actuation mechanism to mitigate hazards.
- [Autonomous Ice Detection and Salt Deployment Robot](https://drive.google.com/file/d/17ZlVzMXgGTChrUjP7URGmZwl4OO1bvt3/view?usp=sharing)

# EECS 280 Fall (2025): Programming and Introductory Data Structures
https://eecs280.org/

This repository contains the programming projects I completed as part of the EECS 280 (Foundations of Computer Science and Programming) course at the University of Michigan. EECS 280 is a second-semester foundational programming course that focuses on essential computer science concepts and programming skills using C++.

Throughout the course, I worked on a series of projects to deepen my understanding of various topics, including data structures, algorithms, recursion, and object-oriented programming. The course emphasized writing correct and maintainable code, testing, and debugging skills, and the use of C++ language features such as classes, templates, and exceptions.

**Projects Included:**
- Statistics Tool - Implemented a two-sample statistical analysis tool.
- Computer Vision - Developed an image resizing algorithm without distortion. 
- Euchre Game - Simulated the Euchre card game, a popular game in Michigan. 
- Machine Learning - Built a tool to automatically categorize EECS 280 forum posts.
- Text Editor - Created a terminal-based text editor with interactive file manipulation.
- Binary Search Tree - Implemented a map using a binary search tree.

**Key Skills Developed:**
- Linked lists, stacks, queues, binary trees.
- Recursion & Functional Abstraction.
- Data Abstraction, Inheritance, Polymorphism.
- Dynamic resource management and memory handling in C++.
- Testing, debugging, and writing maintainable code.

# Automated Bird Counting (CNN)
- Trained CNN (Python) to detect and count Kolea birds (85% accuracy).
<img width="554" height="380" alt="Screenshot 2025-10-12 at 11 31 41 AM" src="https://github.com/user-attachments/assets/2fdbdc83-9071-4385-aa4d-fd987fb417a9" />
