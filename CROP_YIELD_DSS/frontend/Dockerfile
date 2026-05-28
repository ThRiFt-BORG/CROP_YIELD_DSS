FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

EXPOSE 3000

# Serve using Vite preview or serve
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
