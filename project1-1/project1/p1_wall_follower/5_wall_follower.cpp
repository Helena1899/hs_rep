/**
 * File: wall_follower.cpp
 *
 * Controls robot to follow a wall. 
 */

#include <iostream>
#include <cmath>

#include <signal.h>

#include <mbot_bridge/robot.h>

#include <mbot_lib/behaviors.h>
#include <mbot_lib/controllers.h>
#include <mbot_lib/utils.h>


bool ctrl_c_pressed;
void ctrlc(int)
{
    ctrl_c_pressed = true;
}


int main(int argc, const char *argv[])
{
    signal(SIGINT, ctrlc);
    signal(SIGTERM, ctrlc);

    // Initialize the robot.
    mbot_bridge::MBot robot;
    // Create empty vectors to store the scan data.
    std::vector<float> ranges;
    std::vector<float> thetas;

    float setpoint = 0.5;  // The goal distance from the wall in meters
    float scaling = 1;
    float kp = -0.5;
    float error = 0.1;

    while (true) {

        // *** Task: Implement wall following *** //
        // This function gets the Lidar scan data.
        robot.readLidarScan(ranges, thetas);

        float min_idx = findMinNonzeroDist(ranges);
        float dist_to_wall = ranges[min_idx];
        float angle_to_wall = thetas[min_idx];

        std::vector<float> driveVector = computeWallFollowerCommand(ranges,thetas);

        std::cout << "Drive Command: vx=" << driveVector[0] << ", vy=" << driveVector[1] << ", wtheta=" << driveVector[2] << std::endl;
        
        // *** Task 2: Implement the Follow Me controller *** //
        robot.drive(driveVector[0], driveVector[1], 0);
        // *** End student code *** //

        if (ctrl_c_pressed) break;
    }

    // Stop the robot.
    robot.stop();
    return 0;
}
