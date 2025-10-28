from ament_index_python.resources import has_resource

from launch.actions import DeclareLaunchArgument
from launch.launch_description import LaunchDescription
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description() -> LaunchDescription:
    """
    Generate a launch description optimized for maximum resolution and FPS
    with raw sensor_msgs/Image publishing only (no compression).

    Returns
    -------
        LaunchDescription: the launch description optimized for raw performance
    """
    # parameters
    camera_param_name = "camera"
    camera_param_default = str(0)
    camera_param = LaunchConfiguration(
        camera_param_name,
        default=camera_param_default,
    )
    camera_launch_arg = DeclareLaunchArgument(
        camera_param_name,
        default_value=camera_param_default,
        description="camera ID or name"
    )

    format_param_name = "format"
    format_param_default = "SRGGB16"  # 16-bit Bayer RAW for maximum quality
    format_param = LaunchConfiguration(
        format_param_name,
        default=format_param_default,
    )
    format_launch_arg = DeclareLaunchArgument(
        format_param_name,
        default_value=format_param_default,
        description="pixel format (SRGGB16 for max quality, YUYV for max FPS)"
    )

    width_param_name = "width"
    width_param_default = str(1920)  # Full HD width
    width_param = LaunchConfiguration(
        width_param_name,
        default=width_param_default,
    )
    width_launch_arg = DeclareLaunchArgument(
        width_param_name,
        default_value=width_param_default,
        description="image width"
    )

    height_param_name = "height"
    height_param_default = str(1080)  # Full HD height
    height_param = LaunchConfiguration(
        height_param_name,
        default=height_param_default,
    )
    height_launch_arg = DeclareLaunchArgument(
        height_param_name,
        default_value=height_param_default,
        description="image height"
    )

    # camera node optimized for raw performance
    composable_nodes = [
        ComposableNode(
            package='camera_ros',
            plugin='camera::CameraNode',
            parameters=[{
                "camera": camera_param,
                "width": width_param,
                "height": height_param,
                "format": format_param,
                "role": "raw",  # Use raw stream role for maximum FPS
                "enable_compression": False,  # Disable compression for max performance
                "qos_reliability": "best_effort",  # Use best effort for max throughput
            }],
            extra_arguments=[{'use_intra_process_comms': True}],
        ),
    ]

    # optionally add ImageViewNode to show camera image
    if has_resource("packages", "image_view"):
        composable_nodes += [
            ComposableNode(
                package='image_view',
                plugin='image_view::ImageViewNode',
                remappings=[('/image', '/camera/image_raw')],
                extra_arguments=[{'use_intra_process_comms': True}],
            ),
        ]

    # composable nodes in single container
    container = ComposableNodeContainer(
        name='camera_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=composable_nodes,
    )

    return LaunchDescription([
        container,
        camera_launch_arg,
        format_launch_arg,
        width_launch_arg,
        height_launch_arg,
    ])
