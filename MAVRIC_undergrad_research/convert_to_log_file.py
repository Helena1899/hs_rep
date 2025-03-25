# to run this program use: python3 convert_to_log.py <input_file> <output_file>

import sys
import numpy as np
import math


# Function to perform cubic interpolation
def smooth(x, y, xp, yp, t):
    a = 2 * x - 2 * y + xp + yp
    b = -3 * x + 3 * y - 2 * xp - yp
    c = xp
    d = x
    return a * t * t * t + b * t * t + c * t + d


# Function to generate a range of values
def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


# Function to interpolate motion data from the input file
def interpolate(filename, trans_per_sec=0.5, rot_per_sec=25):
    with open(filename) as f:
        lines = []
        for line in f:
            if line.startswith('#'):  # Skip comment lines
                continue
            # Split the line and ignore the first column (timestamp)
            values = line.split()
            lines.append([float(x) for x in values[1:]])  # Skip timestamp (1st column)

    frames = []

    for k in range(0, len(lines) - 1):
        if k == 0:
            ii = [a * 2 - b for a, b in zip(lines[k], lines[k + 1])]
        else:
            ii = lines[k - 1]

        i = lines[k]    
        j = lines[k + 1]

        if k == len(lines) - 2:
            jj = [b * 2 - a for a, b in zip(lines[k], lines[k + 1])]
        else:
            jj = lines[k + 2]

        dist = math.sqrt((i[0] - j[0]) ** 2 + (i[1] - j[1]) ** 2 + (i[2] - j[2]) ** 2)
        angle = max(abs(i[3] - j[3]), abs(i[4] - j[4]))

        duration = max(dist / trans_per_sec, angle / rot_per_sec)

        for t in frange(0, 1, 1 / (duration * 30)):
            frames.append([smooth(a, b, (b - c) * 0.5, (d - a) * 0.5, t) for a, b, c, d in zip(i, j, ii, jj)])

    print('frames:', len(frames))
    return frames


# Convert quaternion to a 3x3 rotation matrix
def quaternion_to_matrix(qx, qy, qz, qw):
    rmat = np.eye(3)

    rmat[0, 0] = 1 - 2*(qy**2 + qz**2)
    rmat[0, 1] = 2*(qx*qy - qz*qw)
    rmat[0, 2] = 2*(qx*qz + qy*qw)

    rmat[1, 0] = 2*(qx*qy + qz*qw)
    rmat[1, 1] = 1 - 2*(qx**2 + qz**2)
    rmat[1, 2] = 2*(qy*qz - qx*qw)

    rmat[2, 0] = 2*(qx*qz - qy*qw)
    rmat[2, 1] = 2*(qy*qz + qx*qw)
    rmat[2, 2] = 1 - 2*(qx**2 + qy**2)

    return rmat


# Main function to process frames and write output to a file
def main(argv):
    frames = interpolate(argv[1])

    with open(argv[2], mode='w') as ff:
        for i in range(0, len(frames)):
            # Unpack translation and quaternion (tx, ty, tz, qx, qy, qz, qw)
            tx, ty, tz, qx, qy, qz, qw = frames[i]

            # Convert quaternion to rotation matrix (3x3)
            rmat = quaternion_to_matrix(qx, qy, qz, qw)

            # Convert rmat to a 4x4 matrix
            rmat_4x4 = np.eye(4)
            rmat_4x4[0:3, 0:3] = rmat

            # Create the translation matrix (4x4)
            tmat = np.eye(4)
            tmat[0:3, 3] = np.array([tx, ty, tz])

            # Create the matrix to handle the camera inversion
            zz = np.eye(4)
            zz[0, 0] = -1
            zz[2, 2] = -1

            # Compute the final transformation matrix
            m = np.dot(np.linalg.inv(np.dot(rmat_4x4, tmat)), zz)

            # Write the transformation matrix to the output file
            ff.write('{0} {1} {2}\n'.format(i, i, i + 1))
            ff.write('{0} {1} {2} {3}\n'.format(m[0][0], m[0][1], m[0][2], m[0][3]))
            ff.write('{0} {1} {2} {3}\n'.format(m[1][0], m[1][1], m[1][2], m[1][3]))
            ff.write('{0} {1} {2} {3}\n'.format(m[2][0], m[2][1], m[2][2], m[2][3]))
            ff.write('{0} {1} {2} {3}\n'.format(m[3][0], m[3][1], m[3][2], m[3][3]))


# Entry point of the program
if __name__ == "__main__":

    from sys import argv

    if (len(argv) < 3):
        print('Usage: {0} <input key poses> <output>'.format(argv[0]))
        exit(0)

    main(argv)

