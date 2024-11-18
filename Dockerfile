FROM python:3.12

WORKDIR /app


RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update \
    apt-get install -y binutils libpq-dev gdal-bin libgdal-dev cmake
COPY . /app

RUN cd gdal-3.10.0 \
    mkdir -p build && cd build 
WORKDIR /app/gdal-3.10.0/build
RUN cmake .. \
    cmake --build . -j 8 \
    cmake --build . --target install \
    ln -s /usr/local/lib/libgdal.so.36.3.10.0  /usr/lib/libgdal.so \
    ln -s /usr/local/lib/libgdal.so.36 /usr/lib/libgdal.so.36 \
    pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app



EXPOSE 9876

CMD ["/bin/bash", "/app/entrypoint.sh"]