FROM node:21.7-alpine AS base

RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package*.json ./
RUN npm ci
COPY . .

CMD npm run dev
# CMD ["npm", "run", "build", "start"]

# RUN npm run build

# CMD ["npm", "run", "start"]
