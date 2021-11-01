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
	autoconf automake \
	libceres-dev \
	libdw-dev

RUN apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y build-essential python3.8 python3.8-distutils

RUN rm -rf /var/lib/apt/lists/*

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user

RUN python -m pip install --upgrade pip; python -m pip install python-igraph==0.8
ENV KALIBR_WORKSPACE /home/user/kalibr_workspace

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

RUN mkdir -p /home/user/workspace
RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3.8 get-pip.py && \
	rm get-pip.py

RUN python3.8 -m pip install --user pillow pyyaml

COPY --chown=user:sudo docker/calibrate/imu/ /home/user/workspace/imu
RUN chmod +x /home/user/workspace/imu/run.sh

# Copy camera_imu related files.
COPY --chown=user:sudo docker/calibrate/camera_imu/ /home/user/workspace/camera_imu
RUN chmod +x /home/user/workspace/camera_imu/run.sh

# Copy General files.
COPY docker/calibrate/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/calibrate/convert_format.py /home/user/workspace/convert_format.py
COPY docker/calibrate/extract_calibration.py /home/user/workspace/extract_calibration.py
COPY docker/calibrate/create_target.py /home/user/workspace/create_target.py


ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]

