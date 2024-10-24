/**
 * File: utils.cpp
 * 
 * Sources for functions for handling common tasks like working with geometry and interpreting lidar data.
 */

#include <mbot_lib/utils.h>
#include <iostream>
#include <vector>

std::vector<float> rayConversionCartisean(float dist, float angle) 
{
    // *** Task: Implement this function according to the header file *** //
    //float rad = (angle * M_PI)/180;
    std::vector <float> rayCart{float(dist*cos(angle)), float((dist*sin(angle)))};
    return rayCart;
    // *** End student code *** //
}

std::vector<float> rayConversionVector(float angle) 
{
    // *** Task: Implement this function according to the header file *** //
    std::vector <float> rayVector{float(cos(angle)), float(sin(angle)), 0};
    return rayVector;
    // *** End student code *** //
}

int findMinDist(const std::vector<float>& ranges)
{
    // *** Task: Implement this function according to the header file *** //
    int min_index = 0;
    for (int i = 0; i < ranges.size(); i++)
    {
        if (ranges[i] < ranges[min_index])
        {
            min_index = i;
        }
    }
    return min_index;
    // *** End student code *** //
}

int findMinNonzeroDist(const std::vector<float>& ranges)
{
    // *** Task: Implement this function according to the header file *** //
    int min_index = 0;
    while (ranges[min_index] == 0){
        min_index++;
    }
    for (int i = 0; i < ranges.size(); i++)
    {
        if ((ranges[i] < ranges[min_index]) && (ranges[i] != 0)){
            min_index = i;
        }
    }
    return min_index;
    // *** End student code *** //
}

std::vector<float> vectorAdd(const std::vector<float>& v1, const std::vector<float>& v2) 
{
    // *** Task: Implement this function according to the header file *** //
    float x = v1[0] + v2[0];
    float y = v1[1] + v2[1];
    float z = v1[2] + v2[2];
    return std::vector<float>{x,y,z};
    // *** End student code *** //
}

std::vector<float> crossProduct(const std::vector<float>& v1, const std::vector<float>& v2) 
{
    // *** Task: Implement this function according to the header file *** //
    float x = v1[1]*v2[2] - v1[2]*v2[1];
    float y = v1[2]*v2[1] - v1[0]*v2[2];
    float z = v1[0]*v2[1] - v1[1]*v2[0];
    return std::vector<float>{x,y,z};
    // *** End student code *** //
}

void transformVector2D(std::vector<float>& xy, float theta) 
{
    // * Task: Implement this function according to the header file * //
    // Ensure xy has 2 elements
    if (xy.size() != 2) {
        return; // Do nothing if the vector doesn't have exactly two elements
    }

    // Extract the original coordinates
    float x = xy[0];
    float y = xy[1];

    // Compute the rotation using the rotation matrix
    float x_new = x * std::cos(theta) - y * std::sin(theta);
    float y_new = x * std::sin(theta) + y * std::cos(theta);

    // Update the vector with the transformed coordinates
    xy[0] = x_new;
    xy[1] = y_new;
    // * End student code * //
}
