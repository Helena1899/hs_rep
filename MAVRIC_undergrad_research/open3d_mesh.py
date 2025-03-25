import open3d as o3d
import numpy as np
import os

# CameraPose class and read_trajectory function defined in the same file
class CameraPose:
    def __init__(self, meta, mat):
        self.metadata = meta
        self.pose = mat

    def __str__(self):
        return "Pose : " + "\n" + np.array_str(self.pose)

def read_trajectory(filename):
    traj = []
    with open(filename, 'r') as f:
        metastr = f.readline()
        while metastr:
            metadata = list(map(int, metastr.split()))
            mat = np.zeros(shape=(4, 4))
            for i in range(4):
                matstr = f.readline()
                mat[i, :] = np.fromstring(matstr, dtype=float, sep=' \t')
            traj.append(CameraPose(metadata, mat))
            metastr = f.readline()
    return traj

# Adjust the TSDF volume integration and implement batch processing
def integrate_tsdf_volume(camera_poses, color_files, depth_files, color_path, depth_path, batch_size=5):
    # Initialize the ScalableTSDFVolume with adjusted parameters
    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=4.0 / 1024.0,  # Reduced voxel size for higher resolution
        sdf_trunc=0.02,  # Reduced truncation distance for better accuracy
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8
    )

    # Modify the intrinsic parameters to match 1280x720 resolution
    intrinsic = o3d.camera.PinholeCameraIntrinsic()
    intrinsic.set_intrinsics(1280, 720,  # width, height
                             615.0, 615.0,  # fx, fy (focal length)
                             640.0, 360.0)  # cx, cy (principal point)

    # Process in smaller batches
    num_frames = len(camera_poses)
    for batch_start in range(0, num_frames, batch_size):
        batch_end = min(batch_start + batch_size, num_frames)
        print(f"Processing frames {batch_start} to {batch_end - 1}...")

        # Process each frame in the batch
        for i in range(batch_start, batch_end):
            print(f"Integrating {i}-th image into the volume.")
            
            # Read the color and depth images
            color = o3d.io.read_image(f"{color_path}/{color_files[i]}")
            depth = o3d.io.read_image(f"{depth_path}/{depth_files[i]}")
            
            # Create RGBD image
            rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
                color, depth, depth_trunc=4.0, convert_rgb_to_intensity=False
            )
            
            # Integrate into the TSDF volume
            volume.integrate(
                rgbd,
                intrinsic,
                np.linalg.inv(camera_poses[i].pose)
            )

        # Extract a mesh after processing the batch
        print(f"Extract a triangle mesh from the volume after processing frames {batch_start} to {batch_end - 1}.")
        mesh = volume.extract_triangle_mesh()
        mesh.compute_vertex_normals()

        # Visualize the extracted mesh
        o3d.visualization.draw_geometries([mesh],
                                          front=[0.5297, -0.1873, -0.8272],
                                          lookat=[2.0712, 2.0312, 1.7251],
                                          up=[-0.0558, -0.9809, 0.1864],
                                          zoom=0.47)
        return mesh

# Main function to run the integration process
def main():
    # Load camera poses from a log file
    camera_poses = read_trajectory("/home/jetson/Documents/RTAB-Map/exported_color/odometry.log")

    # Define paths for color and depth images
    color_path = "/home/jetson/Documents/RTAB-Map/exported_color/rgb"  # Folder with color images
    depth_path = "/home/jetson/Documents/RTAB-Map/exported_color/depth"  # Folder with depth images

    # Retrieve all the files in color and depth folders
    color_files = [f for f in os.listdir(color_path) if f.endswith(('.jpg', '.png'))]
    depth_files = [f for f in os.listdir(depth_path) if f.endswith(('.png', '.jpg'))]

    # Sort files by name to align corresponding color and depth images
    color_files.sort()
    depth_files.sort()

    # Ensure there are the same number of color and depth files
    if len(color_files) != len(depth_files):
        print(f"Warning: Number of color images ({len(color_files)}) and depth images ({len(depth_files)}) do not match!")
        return

    # Call the function to integrate TSDF volume and extract the mesh
    integrate_tsdf_volume(camera_poses, color_files, depth_files, color_path, depth_path)

if __name__ == "__main__":
    main()
