# Pull the latest nodeJS image
FROM node:latest

# Set a working directory for use in the CMD, ENTRYPOINT, ADD and RUN commands
WORKDIR /app

# Copy the application files
COPY . .

# Install dependancies
RUN npm install

# Setup the pixel streaming git repository used to render pixel streaming
RUN npm run setup

# Expose the port the development server listens on
EXPOSE 8081

# Start the server on development mode
CMD ["npm", "run", "dev"]