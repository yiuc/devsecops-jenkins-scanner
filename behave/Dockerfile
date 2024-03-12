FROM public.ecr.aws/docker/library/python:3.10-slim AS installer-image
WORKDIR /app
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update -y 2>/dev/null >/dev/null && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install -y \
    build-essential \
    curl 2>/dev/null >/dev/null \
    && rm -rf /var/lib/apt/lists/*
ADD requirements.txt ./
RUN pip install --upgrade -q -q pip && \
    pip install --user --upgrade -q -q pip && pip install --user -q -q -r requirements.txt

FROM public.ecr.aws/docker/library/python:3.10-slim
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update -y 2>/dev/null >/dev/null && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq upgrade -y 2>/dev/null >/dev/null && \
    DEBIAN_FRONTEND=noninteractive apt install -qq -y curl git unzip 2>/dev/null >/dev/null && \
    addgroup --gid 8000 bddtest && \
    adduser --uid 8000 --gid 8000 --disabled-password --gecos "" bddtest
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install
USER bddtest
WORKDIR /home/bddtest/
COPY --chown=bddtest:bddtest --from=installer-image /root/.local /home/bddtest/.local/
ENV PATH=/home/bddtest/.local/bin:$PATH
