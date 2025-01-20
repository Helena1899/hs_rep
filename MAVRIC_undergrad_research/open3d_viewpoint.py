# reads the point_cloud.ply data and displays it in a 3D viewer

import open3d as o3d
import numpy as np

print("Load a ply point cloud, print it, and render it")
#ply_point_cloud = o3d.data.PLYPointCloud()
pcd = o3d.io.read_point_cloud('point_cloud.ply')


# Add a coordinate frame at the origin (optional)
origin = np.array([0, 0, 0])
coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=origin)

o3d.visualization.draw_geometries([pcd, coordinate_frame],
                                    )