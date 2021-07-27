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

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py

RUN pip3 install open3d scipy numpy PyYAML && rm -rf /root/.cache

RUN git clone https://github.com/stevenlovegrove/Pangolin.git /root/pangolin
RUN cd /root/pangolin && mkdir /root/pangolin/build && cd /root/pangolin/build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release && \
  cmake --build . && \
  make install && rm -rf /root/pangolin/

RUN git clone https://github.com/StrayRobots/ORB_SLAM3.git /root/orbslam && \
  cd /root/orbslam && git checkout 7db29949f898339ed17e8eaa68f75599e43bca5d

RUN cd /root/orbslam/Thirdparty/DBoW2 && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release \
  && make -j4

RUN cd /root/orbslam/Thirdparty/g2o/ && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release && make -j4

RUN cd /root/orbslam/Vocabulary && tar -xf ORBvoc.txt.tar.gz

RUN mkdir /root/workspace
WORKDIR /root/workspace

RUN cd /root/orbslam/ && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && \
  make -j2 o3d

COPY ./entrypoint.sh /root/workspace/entrypoint.sh
COPY integrate.py /root/workspace/integrate.py
COPY make_settings.py /root/workspace/make_settings.py
COPY default_settings.yaml /root/workspace/default_settings.yaml

ENTRYPOINT ["/root/workspace/entrypoint.sh"]

