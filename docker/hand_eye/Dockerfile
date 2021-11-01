FROM nvidia/opengl:base-ubuntu18.04


RUN apt-get update && apt-get install -y gnupg2

RUN echo "deb http://packages.ros.org/ros/ubuntu bionic main" > /etc/apt/sources.list.d/ros1-latest.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
ENV ROS_DISTRO melodic

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y ros-melodic-ros-core

RUN apt-get install -y \
    	python-setuptools \
	python-rosinstall \
	libeigen3-dev \
	libboost-all-dev \
	doxygen \
	libopencv-dev \
	ros-melodic-vision-opencv \
	ros-melodic-cmake-modules \
	libpoco-dev \
	python3-matplotlib \
	python3-pip \
	libtbb-dev \
	libblas-dev \
	liblapack-dev \
	python-catkin-tools \
	python-tk \
	python-scipy \
	libtool \
	wget \
	autoconf \
	automake \
	libdw-dev\
	libv4l-dev \
	libglvnd-dev \
	build-essential \
	libsuitesparse-dev \
	libgtk2.0-dev \
	libyaml-cpp-dev \
	ros-melodic-tf2 \
	ros-melodic-tf2-py \
	ros-melodic-tf \
	python-matplotlib \
	libcanberra-gtk-module \
	libcanberra-gtk3-module

RUN rm -rf /var/lib/apt/lists/*

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user

RUN mkdir -p /home/user/workspace
RUN python3 -m pip install --user pillow pyyaml

# Build hand eye calibration
ENV WORKSPACE=/home/user/workspace
ENV ROS_WORKSPACE=/home/user/workspace/ws
RUN mkdir -p $ROS_WORKSPACE/src

RUN cd $ROS_WORKSPACE/ && catkin init && catkin config --merge-devel && \
	catkin config --extend /opt/ros/melodic && \
	catkin config --cmake-args -DCMAKE_BUILD_TYPE=Debug
RUN pip3 install google-apputils
RUN cd $ROS_WORKSPACE/src && git clone https://github.com/ardiya/hand_eye_calibration &&\
	wstool init && wstool merge hand_eye_calibration/all_dependencies.rosinstall && \
	wstool update -j 8 --continue-on-error
RUN cd $ROS_WORKSPACE/ && catkin build hand_eye_calibration hand_eye_calibration_target_extractor hand_eye_calibration_batch_estimation

COPY --chown=user:sudo docker/hand_eye/run.sh /home/user/workspace/run.sh
COPY --chown=user:sudo docker/hand_eye/create_bag.py /home/user/workspace/create_bag.py
COPY --chown=user:sudo docker/hand_eye/convert_target.py /home/user/workspace/convert_target.py
RUN chmod +x $WORKSPACE/run.sh

ENTRYPOINT ["/home/user/workspace/run.sh"]

