# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Copy package.json and package-lock.json first so we can do an install
COPY package*.json ./

# Install your dependencies
RUN npm install

# Copy the rest of your React app
COPY . .

# Expose the port create-react-app runs on
EXPOSE 3000

# Start the development server
CMD ["npm", "start"]