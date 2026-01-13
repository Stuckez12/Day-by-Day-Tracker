FROM node:22.16.0

WORKDIR /app

COPY . .
RUN npm ci



EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "--port", "3000"]
