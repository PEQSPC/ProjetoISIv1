# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Build argument for API URL (required at build time for Vite)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Copy package files
COPY package.json yarn.lock* package-lock.json* ./

# Install dependencies
RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    else echo "Lockfile not found." && exit 1; \
    fi

# Copy source code
COPY . .

# Build the application (VITE_API_URL is baked into the bundle)
RUN npm run build || yarn build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Create proper nginx configuration for SPA with correct MIME types
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name iot-simulator.local;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    # Handle static assets with correct MIME types
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]