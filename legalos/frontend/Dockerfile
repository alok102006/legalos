FROM node:18-alpine

WORKDIR /app

# Copy dependency configs
COPY package*.json ./

# Install packages
RUN npm install

# Copy application source
COPY . .

# Expose Vite local development port
EXPOSE 5173

# Execute dev server binding to all interfaces
CMD ["npm", "run", "dev", "--", "--host"]
