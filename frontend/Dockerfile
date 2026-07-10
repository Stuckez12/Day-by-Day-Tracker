FROM node:22.11-alpine AS base

WORKDIR /app

RUN apk update && apk upgrade --no-cache
COPY package*.json ./

RUN npm install
COPY . .

FROM base AS dev
CMD ["npm", "run", "dev"]

FROM base AS prod

RUN npm run build

CMD ["sh", "-c", "npm run start"]
