FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
  build-essential \
  git \
  xorg-dev \
  libglu1-mesa-dev \
  libpython2.7-dev \
  python3.8-dev \
  python3.8-distutils \
  cmake \
  libglew-dev \
  libopencv-dev \
  libboost-dev \
  libeigen3-dev \
  libssl-dev \
  libomp-dev \
  libboost-serialization-dev \
  qtbase5-dev \
  libqt5opengl5-dev \
  libcgal-dev \
  libsuitesparse-dev \
  libatlas-base-dev \
  libgflags-dev \
  libfreeimage-dev \
  libgoogle-glog-dev \
  libboost-graph-dev \
  libboost-test-dev \
  libboost-system-dev \
  libboost-filesystem-dev \
  libboost-program-options-dev \
  wget \
  unzip

RUN rm -rf /var/lib/apt/lists/*

RUN git clone https://ceres-solver.googlesource.com/ceres-solver /tmp/ceres-solver/ && \
  cd /tmp/ceres-solver && \
  git checkout $(git describe --tags) && \
  mkdir build && cd build && \
  cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
  make -j && \
  make install && \
  rm -rf /tmp/ceres-solver

RUN git clone https://github.com/colmap/colmap /tmp/colmap
RUN cd /tmp/colmap && git checkout dev && mkdir build && cd build && \
  cmake .. -DCMAKE_BUILD_TYPE=Release && \
  make -j && \
  make install && \
  rm -rf /tmp/colmap

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

COPY --chown=user:sudo straylib /tmp/straylib
WORKDIR /tmp/straylib
RUN python3.8 setup.py bdist_egg --exclude-source-files
RUN wheel convert $(find dist/straylib-*.egg)
RUN pip3.8 install "$(basename $(find straylib-*.whl))"
RUN rm -rf /tmp/straylib

RUN pip3 install --user open3d==0.14.1 opencv-python scipy numpy PyYAML click trimesh requests && rm -rf /user/.cache

RUN mkdir /home/user/workspace
WORKDIR /home/user/workspace

COPY docker/integrate/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/integrate/run_sfm.py /home/user/workspace/run_sfm.py
COPY docker/integrate/combine_trajectories.py /home/user/workspace/combine_trajectories.py
COPY docker/integrate/utils.py /home/user/workspace/utils.py
COPY docker/validate_license.py /home/user/workspace/validate_license.py
COPY docker/integrate/pipeline.mg /home/user/workspace/pipeline.mg
COPY docker/orbslam/integrate.py /home/user/workspace/integrate.py
COPY docker/orbslam/integrate_pointcloud.py /home/user/workspace/integrate_pointcloud.py

ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]
CMD []

