FROM node:15-alpine as builder

WORKDIR /app

COPY ./package-lock.json ./package.json ./
RUN npm ci

COPY ./ ./
RUN npm run build

FROM node:15-alpine

WORKDIR /app
RUN npm -g i serve

COPY --from=builder /app/public /app/public

ENTRYPOINT [ "serve" ]
CMD [ "-l", "80", "-s", "/app/public" ]


