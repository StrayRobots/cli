#!/bin/bash
set -e

cd $ROS_WORKSPACE
source devel/setup.bash

intrinsics=/home/user/data/camera.yaml
target_yaml=/home/user/workspace/target.yaml
hand_eye_target_yaml=/tmp/hand_eye_target.yaml
poses_timestamped=tf_poses_timestamped.csv
camera_poses_timestamped=camera_poses_timestamped.csv
camera_aligned=camera_aligned.csv
tf_aligned=tf_aligned.csv
time_offset=time_offset.csv

python $WORKSPACE/create_bag.py --scene /home/user/data/ --out /tmp/bag.bag
python $WORKSPACE/convert_target.py --target $target_yaml --out /tmp/hand_eye_target.yaml


mkdir /tmp/hand_eye_calibration
pushd /tmp/hand_eye_calibration
rosrun hand_eye_calibration tf_to_csv.py --bag /tmp/bag.bag \
  --tf_source_frame hand_frame \
  --tf_target_frame base_frame \
  --csv_output_file $poses_timestamped

pose_count=$(cat $poses_timestamped | wc -l)
if [ "$pose_count" = "0" ];
then
  echo "Could not find any valid poses. Check the transformations and frames."
  echo "It could be that the timestamps don't match or the frames of the transformations are wrong."
  exit 1
fi

rosrun hand_eye_calibration target_extractor_interface.py \
  --bag /tmp/bag.bag \
  --calib_file_camera $intrinsics \
  --calib_file_target $hand_eye_target_yaml \
  --image_topic /image \
  --output_file $camera_poses_timestamped

rosrun hand_eye_calibration compute_aligned_poses.py \
  --poses_B_H_csv_file $poses_timestamped \
  --poses_W_E_csv_file $camera_poses_timestamped \
  --aligned_poses_B_H_csv_file $tf_aligned \
  --aligned_poses_W_E_csv_file $camera_aligned \
  --time_offset_output_csv_file $time_offset

rosrun hand_eye_calibration compute_hand_eye_calibration.py \
  --aligned_poses_B_H_csv_file $tf_aligned \
  --aligned_poses_W_E_csv_file $camera_aligned \
  --time_offset_input_csv_file $time_offset \
  --calibration_output_json_file calibration.json \
  --visualize True

rosrun hand_eye_calibration_batch_estimation batch_estimator \
	--v 1 \
	--pose1_csv $poses_timestamped \
	--pose2_csv $camera_poses_timestamped \
	--init_guess_file calibration.json \
	--output_file calibration_optimized.json

popd

mv /tmp/hand_eye_calibration/calibration.json /home/user/data/hand_eye_calibration.json
mv /tmp/hand_eye_calibration/calibration_optimized.json /home/user/data/hand_eye_calibration_optimized.json
