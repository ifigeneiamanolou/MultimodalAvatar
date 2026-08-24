FROM node:latest

WORKDIR /app

COPY . .

RUN npm install

EXPOSE 8081

CMD ["npx", "expo", "start"]