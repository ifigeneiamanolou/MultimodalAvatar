# Pull the latest nodeJS image
FROM node:latest

# Set a working directory for use in the CMD, ENTRYPOINT, ADD and RUN commands
WORKDIR /app

# Copy the application files
COPY . .

# Install dependancies
RUN npm install

# Expose the port the development server listens on
EXPOSE 8081

# Start the server
CMD ["npx", "expo", "start"]