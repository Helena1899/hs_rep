/**
 * File: drive_star.cpp
 *
 * Code to drive in a five-pointed star shape without turning. 
 */

#include <iostream>
#include <cmath>

#include <signal.h>

#include <mbot_bridge/robot.h>

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

    // *** Task: Drive in a five pointed star *** //

    std::vector<float> a = rayConversionVector(0);
    robot.drive(0.8*a[0], 0.8*a[1], 0);
    sleepFor(0.6);
    robot.stop();
    sleepFor(0.6);

    std::vector<float> b = rayConversionVector(-.8*M_PI);
    robot.drive(0.8*b[0], 0.8*b[1], 0);
    sleepFor(0.6);
    robot.stop();
    sleepFor(0.6);
    
    std::vector<float> c = rayConversionVector(.4*M_PI);
    robot.drive(0.8*c[0], 0.8*c[1] , 0);
    sleepFor(0.6);
    robot.stop();
    sleepFor(0.6);

    std::vector<float> d = rayConversionVector(-.4*M_PI);
    robot.drive(0.8*d[0], 0.8*d[1], 0);
    sleepFor(0.6);
    robot.stop();
    sleepFor(0.6);
    
    std::vector<float> e = rayConversionVector(.8*M_PI);
    robot.drive(0.8*e[0], 0.8*e[1] , 0);
    sleepFor(0.6);
    robot.stop();
    sleepFor(0.6);
    
    // *** End student code *** //

    // Stop the robot.
    robot.stop();
    return 0;
}