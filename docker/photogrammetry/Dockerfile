FROM nvidia/cuda:10.2-base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
  git \
  xorg-dev \
  libglu1-mesa-dev \
  libpython2.7-dev \
  python-opencv \
  python3.8-dev \
  python3.8-distutils \
  cmake \
  python-pip \
  libglew-dev \
  libopencv-dev \
  libboost-dev \
  libeigen3-dev \
  libssl-dev \
  libomp-dev \
  libboost-serialization-dev \
  wget \
  unzip

RUN rm -rf /var/lib/apt/lists/*

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user
WORKDIR /home/user

ENV PATH="/home/user/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.8 get-pip.py
RUN rm get-pip.py

RUN pip3 install --user open3d opencv-python scipy numpy PyYAML click trimesh && rm -rf /user/.cache

RUN git clone https://github.com/stevenlovegrove/Pangolin.git --recursive /home/user/pangolin
RUN cd /home/user/pangolin && git checkout dd801d244db3a8e27b7fe8020cd751404aa818fd && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/home/user/opt/ && \
  cmake --build . && \
  make install

#TODO: fix commit once merged: https://github.com/StrayRobots/ORB_SLAM3/pull/3
RUN git clone https://github.com/StrayRobots/ORB_SLAM3.git /home/user/orbslam && \
  cd /home/user/orbslam && git fetch && git checkout rgb-slam

RUN cd /home/user/orbslam/Thirdparty/DBoW2 && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release \
  && make -j2

RUN cd /home/user/orbslam/Thirdparty/g2o/ && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release && make -j2

RUN cd /home/user/orbslam/Vocabulary && tar -xf ORBvoc.txt.tar.gz

RUN cd /home/user/orbslam/ && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && \
  make -j2 rgb


RUN mkdir /home/user/workspace
WORKDIR /home/user/workspace

RUN wget https://github.com/alicevision/meshroom/releases/download/v2021.1.0/Meshroom-2021.1.0-linux-cuda10.tar.gz
RUN chown user:sudo /home/user/workspace/Meshroom-2021.1.0-linux-cuda10.tar.gz
RUN tar -xf /home/user/workspace/Meshroom-2021.1.0-linux-cuda10.tar.gz

COPY docker/photogrammetry/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/photogrammetry/filter_images.py /home/user/workspace/filter_images.py
COPY docker/photogrammetry/prepare_scene.py /home/user/workspace/prepare_scene.py
COPY docker/photogrammetry/default_settings.yaml /home/user/workspace/default_settings.yaml
COPY docker/photogrammetry/make_settings.py /home/user/workspace/make_settings.py
COPY docker/photogrammetry/combine_trajectories.py /home/user/workspace/combine_trajectories.py




ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]
CMD []

