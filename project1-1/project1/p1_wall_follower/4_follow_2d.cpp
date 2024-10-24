/**
 * File: follow_2d.cpp
 *
 * Controls the robot to maintain a given distance to the nearest wall.
 *
 * This code finds the distance to the nearest wall in the Lidar scan. It
 * applies a control to the robot in the direction of the wall using the angle
 * to the scan.
 */

#include <cmath>
#include <iostream>

#include <signal.h>

#include <mbot_bridge/robot.h>

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

    // We will store the Lidar scan data in these vectors.
    std::vector<float> ranges;
    std::vector<float> thetas;

    // *** Task 1: Adjust these values appropriately ***

    float setpoint = 0.8;  // The goal distance from the wall in meters
    float scaling = 0.3;
    float kp = 1.0;
    float error = 0;

    // *** End student code *** //

    while (true) {
        // This function gets the Lidar scan data.
        robot.readLidarScan(ranges, thetas);

        // Get the distance to the wall.
        float min_dist = findMinDist(ranges);
        float min_idx = findMinNonzeroDist(ranges);
        float dist_to_wall = ranges[min_idx];
        float angle_to_wall = thetas[min_idx];

        // *** Task 2: Implement the 2D Follow Me controller ***
        // Hint: Look at your code from follow_1D
        // Hint: When you compute the velocity command, you might find the functions
        // rayConversionVector helpful!

        std::vector<float> v_direction = rayConversionVector(angle_to_wall);

        std::vector<float> dist = rayConversionCartisean(dist_to_wall, angle_to_wall);

        float direction = bangBangControl(dist_to_wall, setpoint, scaling, 0.05);
        float pX = pControl(dist[0], setpoint, kp);
        float pY = pControl(dist[1], setpoint, kp);

        robot.drive(direction * v_direction[0] * pX, direction * v_direction[1] * pY, 0);
        //robot.drive(0.5*direction * pX, 0.5*direction * pY, 0);
        // *** End Student Code ***

        if (ctrl_c_pressed) break;
    }

    // Stop the robot.
    robot.stop();
    return 0;
}