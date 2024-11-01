# Use Node slim image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy only package.json and package-lock.json first for caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Start the development server
CMD ["npm", "run", "dev"]
