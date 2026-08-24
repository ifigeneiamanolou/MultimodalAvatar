FROM node:latest

WORKDIR /app

COPY . .

RUN npm install

RUN npm run setup

EXPOSE 8081

CMD ["npm", "run", "dev"]