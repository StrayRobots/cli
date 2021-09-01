FROM osrf/ros:kinetic-desktop

RUN apt-get update && apt-get install -y \
    	python-setuptools \
	python-rosinstall \
	libeigen3-dev \
	libboost-all-dev \
	doxygen \
	libopencv-dev \
	ros-kinetic-vision-opencv \
	ros-kinetic-image-transport-plugins \
	ros-kinetic-cmake-modules \
	python-software-properties \
	software-properties-common \
	libpoco-dev \
	python-matplotlib \
	python-scipy \
	python-git \
	python-pip \
	python-tk \
	libtbb-dev \
	libblas-dev \
	liblapack-dev \
	python-catkin-tools \
	libv4l-dev \
	libtool \
	bison \
	flex \
	wget \
	autoconf automake \
	libceres-dev \
	libdw-dev

RUN rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip; python -m pip install python-igraph==0.8
ENV KALIBR_WORKSPACE /kalibr_workspace

RUN mkdir -p $KALIBR_WORKSPACE/src &&\
	cd $KALIBR_WORKSPACE &&\
	catkin init &&\
	catkin config --extend /opt/ros/kinetic &&\
	catkin config --cmake-args -DCMAKE_BUILD_TYPE=Release

WORKDIR "$KALIBR_WORKSPACE"

RUN cd $KALIBR_WORKSPACE/src && git clone https://github.com/StrayRobots/Kalibr.git && \
	cd Kalibr && git checkout 777cda4daafc996da794e5ea2762a7004973cf99

RUN cd $KALIBR_WORKSPACE/src && git clone https://github.com/A1R0B0T/code_utils && git clone https://github.com/gaowenliang/imu_utils

RUN cd $KALIBR_WORKSPACE &&\
	catkin build -DCMAKE_BUILD_TYPE=Release code_utils

RUN cd $KALIBR_WORKSPACE &&\
	catkin build -DCMAKE_BUILD_TYPE=Release imu_utils

RUN cd $KALIBR_WORKSPACE &&\
	catkin build -DCMAKE_BUILD_TYPE=Release -j4

RUN mkdir /root/workspace
RUN python -m pip install pillow pyyaml
COPY ./entrypoint.sh /root/workspace/entrypoint.sh
COPY convert_format.py /root/workspace/convert_format.py
COPY extract_calibration.py /root/workspace/extract_calibration.py
COPY create_target.py /root/workspace/create_target.py
COPY imu/ /root/workspace/imu
RUN chmod +x /root/workspace/imu/run.sh
COPY camera_imu/ /root/workspace/camera_imu
RUN chmod +x /root/workspace/camera_imu/run.sh

ENTRYPOINT ["/root/workspace/entrypoint.sh"]

