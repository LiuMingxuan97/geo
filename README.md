# geo

DockerfileBase 基础镜像，安装gdal和其他c++相关库
Dockerfile 代码执行镜像
镜像启动命令
docker run -itd --name geotranscon -v /mnt/data1/data/lmx_data/geo/data/:/app/data -v /mnt/data1/data/lmx_data/geo/conf/:/app/conf -p 9876:9876 geotranscon:latest  
