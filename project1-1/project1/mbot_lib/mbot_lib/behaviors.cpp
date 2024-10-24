/**
 * File: behaviors.cpp
 * 
 * Sources for high level functions that determine how the robot should move.
 */

#include <mbot_lib/behaviors.h>
#include <iostream>

std::vector<float> computeWallFollowerCommand(const std::vector<float>& ranges, const std::vector<float>& thetas)
{
    // *** Task: Implement this function according to the header file *** //
/*
int min_idx = findMinNonzeroDist(ranges);
    float dist_to_wall = ranges[min_idx];
    float angle_to_wall = thetas[min_idx];
    float kp = -1.5;
    float setpoint = 0.3;
    std::vector<float> zVector = {0, 0, 1};

    //gets the vector to wall in x, y, z (for cross product)
    std::vector<float> direction = rayConversionVector(angle_to_wall);
    std::vector<float> xyCross = crossProduct(direction, zVector);

    //finds dist in x and y (for P-control)
    std::vector<float> xyDist = rayConversionCartisean(dist_to_wall, angle_to_wall);

    float pX = pControl(xyDist[0], setpoint, kp);
    float pY = pControl(xyDist[1], setpoint, kp);
    std::vector<float> pVector = {pX, pY, 0};

    //x and y additions
    std::vector<float> xySum = vectorAdd(xyCross, pVector);

    // Calculate error from desired distance
    float distanceError = dist_to_wall - setpoint;

    // Adjust angular velocity based on distance error
    float wtheta = -kp * distanceError;

    // Return the command vector
    return {pX, pY, wtheta};
    // *** End student code *** //

*/
    int min_idx = findMinNonzeroDist(ranges);
    float dist_to_wall = ranges[min_idx];
    float angle_to_wall = thetas[min_idx];
    float setpoint = 0.3;
    float scaling = 1;
    float kp = 0.75;

    std::vector<float> vectorToWall = rayConversionCartisean(dist_to_wall, angle_to_wall);
    std::vector<float> vectorUp = {0, 0, 1};
    std::vector<float> vectorForward = crossProduct(vectorToWall, vectorUp);

   // float correction = pControl(dist_to_wall, setpoint, kp);
    float direction = bangBangControl(dist_to_wall, setpoint, scaling, 0.05);
    float pX = pControl(vectorToWall[0], setpoint, kp);
    float pY = pControl(vectorToWall[1], setpoint, kp);
    std::vector<float> correction = {pX * direction, pY * direction};
    std::vector<float> finalVector = vectorAdd(vectorForward, correction);
    return finalVector;
}

std::vector<float> computeDriveToPoseCommand(const std::vector<float>& goal, const std::vector<float>& pose)
{   
    // * Task: Implement this function according to the header file * //
    // Ensure both goal and pose have exactly 3 elements (x, y, theta)
    if (goal.size() != 3 || pose.size() != 3) {
        return {0.0, 0.0, 0.0};  // Return zero velocity if input is invalid
    }

    // Compute the difference in x, y, and theta between goal and current pose
    float dx = goal[0] - pose[0];  // Difference in x (linear position in world frame)
    float dy = goal[1] - pose[1];  // Difference in y (linear position in world frame)
    float dtheta = goal[2] - pose[2];  // Difference in theta (orientation)

    // Normalize the angular difference to the range [-pi, pi]
    while (dtheta > M_PI) dtheta -= 2 * M_PI;
    while (dtheta < -M_PI) dtheta += 2 * M_PI;

    // Return the drive command as (vx, vy, wtheta)
    // vx and vy are the linear velocities, wtheta is the angular velocity
    return {dx, dy, dtheta};

    return std::vector<float>();

    // * End student code * //
}

bool isGoalAngleObstructed(const std::vector<float>& goal, const std::vector<float>& pose,
                           const std::vector<float>& ranges, const std::vector<float>& thetas)
{
    // *** Task: Implement this function according to the header file *** //

    return false;

    // *** End student code *** //
}