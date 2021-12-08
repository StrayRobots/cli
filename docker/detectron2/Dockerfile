FROM nvidia/cuda:11.1.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo ninja-build freeglut3-dev
RUN ln -sv /usr/bin/python3 /usr/bin/python


# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user
WORKDIR /home/user
ENV PATH="/home/user/.local/bin:${PATH}"

RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3 get-pip.py && \
	rm get-pip.py

ENV FORCE_CUDA="1"
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

RUN pip install torch==1.9 torchvision==0.10 -f https://download.pytorch.org/whl/cu111/torch_stable.html
RUN pip install git+https://github.com/facebookresearch/detectron2.git@v0.5

RUN mkdir -p /home/user/workspace/
RUN pip install wheel

COPY --chown=user:sudo straylib /tmp/straylib
WORKDIR /tmp/straylib
RUN python setup.py bdist_egg --exclude-source-files
RUN wheel convert $(find dist/straylib-*.egg)
RUN pip install "$(basename $(find straylib-*.whl))"
RUN rm -rf /tmp/straylib

COPY --chown=user:sudo straymodel /tmp/straymodel
WORKDIR /tmp/straymodel
RUN python setup.py bdist_egg --exclude-source-files
RUN wheel convert $(find dist/straymodel-*.egg)
RUN pip install "$(basename $(find straymodel-*.whl))"
RUN rm -rf /tmp/straymodel

ENV FVCORE_CACHE="/tmp"

COPY docker/detectron2/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/validate_license.py /home/user/workspace/validate_license.py 

ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]
CMD []
