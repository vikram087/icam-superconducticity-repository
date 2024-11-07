# Use Node slim image
FROM node:18-slim

# Set working directory
WORKDIR /app

RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Copy only package.json and package-lock.json first for caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Start the development server
CMD ["npm", "run", "dev"]
