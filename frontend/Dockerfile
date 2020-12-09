FROM node:14-alpine

VOLUME [ "/app/node_modules" ]

WORKDIR /app
COPY ./package.json ./yarn.lock ./
RUN yarn

ENTRYPOINT [ "yarn" ]
CMD [ "run", "dev" ]