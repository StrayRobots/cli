
FROM nvidia/cuda:11.1.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo ninja-build freeglut3-dev
RUN ln -sv /usr/bin/python3 /usr/bin/python

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} appuser -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER appuser
WORKDIR /home/appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3 get-pip.py --user && \
	rm get-pip.py

#install straylib
RUN pip install --user https://stray-wheels.nyc3.digitaloceanspaces.com/straylib-0.0.1-py38-none-any.whl
#install straymodel
RUN pip install --user https://stray-wheels.nyc3.digitaloceanspaces.com/straymodel-0.0.1-py38-none-any.whl
# set FORCE_CUDA because during `docker build` cuda is not accessible
ENV FORCE_CUDA="1"
# This will by default build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

#install detectro2
RUN pip install --user git+https://github.com/facebookresearch/detectron2.git@v0.4

# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"

COPY ./entrypoint.sh /home/appuser/entrypoint.sh
ENTRYPOINT ["/home/appuser/entrypoint.sh"]