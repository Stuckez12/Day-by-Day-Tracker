FROM node:21.7-alpine AS base

RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package*.json ./
RUN npm ci
COPY . .

ARG NEXT_PUBLIC_BASE_API_URL
ENV NEXT_PUBLIC_BASE_API_URL=$NEXT_PUBLIC_BASE_API_URL

RUN next build

CMD ["npm", "run", "start"]
