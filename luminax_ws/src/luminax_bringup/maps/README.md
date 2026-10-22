# Maps

Saved maps (`.yaml` + `.pgm`) live here, or anywhere you like.

## Save a map while SLAM is running

With `slam.launch.py` running and after driving the robot around:

```bash
# Option A: Nav2 map saver CLI (recommended)
ros2 run nav2_map_server map_saver_cli -f ~/luminax_ws/src/luminax_bringup/maps/home

# Option B: through slam_toolbox's own serialization (for re-localization)
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: 'home'}}"
```

This produces `home.yaml` and `home.pgm`.

## Use a saved map for navigation

```bash
ros2 launch luminax_bringup navigation.launch.py \
  map:=$HOME/luminax_ws/src/luminax_bringup/maps/home.yaml
```
