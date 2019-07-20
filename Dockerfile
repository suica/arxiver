FROM buildpack-deps:jessie
MAINTAINER https://github.com/suica/arxiver
ENV PATH /usr/local/bin:$PATH

RUN mkdir -p /app
WORKDIR /app
COPY . .
# install requirements
RUN ./install.sh 
ENV SQLITE_DB_ADDR /data/mydb.db
RUN echo 'alias python=python3' >> /root/.bashrc
RUN /bin/bash -c "source /root/.bashrc"
RUN python3 -m pip install -i  https://pypi.doubanio.com/simple/ --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3","app.py" ]
CMD ["bash","async_tasks/www.sh"]

EXPOSE 5000

