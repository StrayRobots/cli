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
	python-pyx \
	libtbb-dev \
	libblas-dev \
	liblapack-dev \
	python-catkin-tools \
	libv4l-dev \
	libtool \
	bison \
	flex \
	wget \
	autoconf automake

RUN rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip; python -m pip install python-igraph==0.8
ENV KALIBR_WORKSPACE /kalibr_workspace

RUN mkdir -p $KALIBR_WORKSPACE/src &&\
	cd $KALIBR_WORKSPACE &&\
	catkin init &&\
	catkin config --extend /opt/ros/kinetic &&\
	catkin config --cmake-args -DCMAKE_BUILD_TYPE=Release

RUN cd $KALIBR_WORKSPACE/src &&\
	git clone https://github.com/StrayRobots/Kalibr.git

RUN cd $KALIBR_WORKSPACE &&\
	catkin build -DCMAKE_BUILD_TYPE=Release -j4

RUN mkdir /root/workspace
RUN python -m pip install pillow pyyaml
COPY docker/calibrate/entrypoint.sh /root/workspace/entrypoint.sh
COPY docker/calibrate/convert_format.py /root/workspace/convert_format.py
COPY docker/calibrate/extract_calibration.py /root/workspace/extract_calibration.py
COPY docker/calibrate/create_target.py /root/workspace/create_target.py

ENTRYPOINT ["/root/workspace/entrypoint.sh"]

