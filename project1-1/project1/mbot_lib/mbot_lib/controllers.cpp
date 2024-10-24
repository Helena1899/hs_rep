#include <mbot_lib/controllers.h>


float bangBangControl(float current, float setpoint, float scaling, float tolerance)
{
    // *** Task: Implement this function according to the header file *** //
    float vel = scaling;
    if (current - setpoint > tolerance)
    {
        return -vel;
    } else if (setpoint - current > tolerance)
    {
        return vel;
    } else {
        return 0.0;
    }
    // *** End student code *** //
}

float pControl(float current, float setpoint, float kp)
{
    // *** Task: Implement this function according to the header file *** //
    float error = setpoint - current;
    return kp * error;
    // *** End student code *** //
}