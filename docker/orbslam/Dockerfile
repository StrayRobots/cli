FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
  git \
  xorg-dev \
  libglu1-mesa-dev \
  libpython2.7-dev \
  python-opencv \
  python3-dev \
  cmake \
  python-pip \
  libglew-dev \
  libopencv-dev \
  libboost-dev \
  libeigen3-dev \
  libssl-dev \
  libomp-dev \
  libboost-serialization-dev \
  wget

RUN rm -rf /var/lib/apt/lists/*

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user
WORKDIR /home/user

ENV PATH="/home/user/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py

RUN pip3 install --user open3d opencv-python scipy numpy PyYAML && rm -rf /user/.cache

RUN git clone https://github.com/stevenlovegrove/Pangolin.git /home/user/pangolin
RUN cd /home/user/pangolin && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/home/user/opt/ && \
  cmake --build . && \
  make install

RUN git clone https://github.com/StrayRobots/ORB_SLAM3.git /home/user/orbslam && \
  cd /home/user/orbslam && git checkout 7db29949f898339ed17e8eaa68f75599e43bca5d

RUN cd /home/user/orbslam/Thirdparty/DBoW2 && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release \
  && make -j10

RUN cd /home/user/orbslam/Thirdparty/g2o/ && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release && make -j10

RUN cd /home/user/orbslam/Vocabulary && tar -xf ORBvoc.txt.tar.gz

RUN cd /home/user/orbslam/ && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && \
  make -j2 o3d

RUN wget https://stray-builds.ams3.digitaloceanspaces.com/straylib/straylib-0.0.1-py36-none-any.whl && \
  pip3 install --user straylib-0.0.1-py36-none-any.whl && rm straylib-0.0.1-py36-none-any.whl #

RUN mkdir /home/user/workspace
WORKDIR /home/user/workspace

COPY ./entrypoint.sh /home/user/workspace/entrypoint.sh
COPY integrate.py /home/user/workspace/integrate.py
COPY integrate_pointcloud.py /home/user/workspace/integrate_pointcloud.py
COPY make_settings.py /home/user/workspace/make_settings.py
COPY default_settings.yaml /home/user/workspace/default_settings.yaml

ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]

