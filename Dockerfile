FROM python:3.7-buster

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true
ENV NODE_PATH                        /node_modules
ENV PATH                             /node_modules/.bin:$PATH

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
        && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
        && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
        && apt-get update \
        && apt-get install -y \
        pandoc \
        rsync \
        nodejs \
        google-chrome-unstable \
        fonts-ipafont-gothic \
        fonts-wqy-zenhei \
        fonts-thai-tlwg \
        fonts-kacst \
        fonts-freefont-ttf \
        --no-install-recommends \
        && rm -rf /var/lib/apt/lists/*

RUN npm i puppeteer decktape \
        # Add user so we don't need --no-sandbox.
        # same layer as npm install to keep re-chowned files from using up several hundred MBs more space
        && groupadd -r mdr && useradd -r -g mdr -G audio,video mdr \
        && mkdir -p /home/mdr/files \
        && chown -R mdr:mdr /home/mdr \
        && chown -R mdr:mdr /node_modules

WORKDIR /home/mdr/files

COPY . /home/mdr/files

RUN python -m pip install --upgrade pip \
        && python -m pip install -r requirements.txt \
        && python setup.py install \
        && cd .. \
        && rm -rf tmp/*

USER mdr

EXPOSE 8123

ENTRYPOINT ["markdownreveal"]

CMD ["presentation.md"]
