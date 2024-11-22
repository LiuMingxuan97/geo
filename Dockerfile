FROM mygeo:base

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 9876

CMD ["/bin/bash", "/app/entrypoint.sh"]
