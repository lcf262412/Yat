FROM python:3.8-slim
WORKDIR /root
COPY yat-master/pkg yat
RUN cd yat && chmod +x install && ./install -F
COPY --from=openjdk:11-jre-slim /usr/local/openjdk-11 /usr/local/openjdk-11
ENV JAVA_HOME=/usr/local/openjdk-11
ENV PATH=$JAVA_HOME/bin:$PATH
ENTRYPOINT ["yat"]
