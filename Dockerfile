# 第一阶段：构建 GDAL
FROM python:3.12 AS builder

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update \
    && apt-get install -y binutils libpq-dev gdal-bin libgdal-dev cmake g++

COPY . /app

WORKDIR /app/gdal-3.10.0
RUN mkdir -p build && cd build \
    && cmake .. \
    && cmake --build . -j 8 \
    && cmake --build . --target install 
    # && ln -s /usr/local/lib/libgdal.so.36.3.10.0 /usr/lib/libgdal.so \
    # && ln -s /usr/local/lib/libgdal.so.36 /usr/lib/libgdal.so.36

# 第二阶段：最终运行镜像
FROM python:3.12

WORKDIR /app

# 从第一阶段复制已编译的 GDAL 库和其他必要文件
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/lib /usr/lib

RUN ln -s /usr/local/lib/libgdal.so.36.3.10.0 /usr/lib/libgdal.so \
    && ln -s /usr/local/lib/libgdal.so.36 /usr/lib/libgdal.so.36

COPY . /app
# 安装 Python 依赖
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple



EXPOSE 9876

CMD ["/bin/bash", "/app/entrypoint.sh"]
