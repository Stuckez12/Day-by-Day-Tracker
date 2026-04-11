FROM node:22.16.0

WORKDIR /app

COPY . .
RUN npm ci

EXPOSE 3000

CMD ["sh", "-c", "npm run build && npx serve -s dist"]
