FROM nvidia/opengl:base-ubuntu18.04

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
RUN python3.8 get-pip.py
RUN rm get-pip.py

RUN pip3 install --user open3d opencv-python scipy numpy PyYAML && rm -rf /user/.cache

RUN git clone https://github.com/stevenlovegrove/Pangolin.git --recursive /home/user/pangolin
RUN cd /home/user/pangolin && git checkout dd801d244db3a8e27b7fe8020cd751404aa818fd && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/home/user/opt/ && \
  cmake --build . && \
  make install

RUN git clone https://github.com/StrayRobots/ORB_SLAM3.git /home/user/orbslam && \
  cd /home/user/orbslam && git checkout defae2b81772dfd613d8c90914c4b1787250beda

RUN cd /home/user/orbslam/Thirdparty/DBoW2 && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release \
  && make -j5

RUN cd /home/user/orbslam/Thirdparty/g2o/ && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release && make -j5

RUN cd /home/user/orbslam/Vocabulary && tar -xf ORBvoc.txt.tar.gz

RUN cd /home/user/orbslam/ && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && \
  make  o3d

COPY --chown=user:sudo straylib /tmp/straylib
WORKDIR /tmp/straylib
RUN python3.8 setup.py bdist_egg --exclude-source-files
RUN wheel convert $(find dist/straylib-*.egg)
RUN pip3.8 install "$(basename $(find straylib-*.whl))"
RUN rm -rf /tmp/straylib

RUN mkdir /home/user/workspace
WORKDIR /home/user/workspace

COPY docker/orbslam/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/orbslam/integrate.py /home/user/workspace/integrate.py
COPY docker/orbslam/integrate_pointcloud.py /home/user/workspace/integrate_pointcloud.py
COPY docker/orbslam/make_settings.py /home/user/workspace/make_settings.py
COPY docker/orbslam/default_settings.yaml /home/user/workspace/default_settings.yaml
COPY docker/validate_license.py /home/user/workspace/validate_license.py 

ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]
CMD []

