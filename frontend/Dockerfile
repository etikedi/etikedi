FROM node:13.12-buster-slim

WORKDIR /app
COPY package.json yarn.lock ./
RUN npm install

COPY . .

CMD ["yarn", "serve"]