FROM python:3.6

RUN pip install --trusted-host pypi.python.org Flask~=0.12

ADD ./examples/docker-agent /agent

# @TODO to be replaced with `pip install pommerman`
ADD . /pommerman
RUN cd /pommerman && pip install .
# end @TODO

EXPOSE 10080

ENV NAME Agent

# Run app.py when the container launches
WORKDIR /agent
ENTRYPOINT ["python"]
CMD ["run.py"]
