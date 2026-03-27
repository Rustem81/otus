# ===========================================
# Development stage (hot reload)
# ===========================================
FROM mirror.gcr.io/node:22-alpine AS development

WORKDIR /app

# Install dependencies (will be cached)
COPY package*.json ./
RUN npm ci --ignore-scripts

# Copy source for initial build
COPY . .

EXPOSE 9000

CMD ["sh", "-c", "npm install && npm run dev"]

# ===========================================
# Build stage
# ===========================================
FROM mirror.gcr.io/node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts

COPY . .
RUN npx quasar prepare
RUN npm run build

# ===========================================
# Production stage
# ===========================================
FROM mirror.gcr.io/nginx:alpine AS production

RUN apk add --no-cache curl gettext

# Copy static files
COPY --from=builder /app/dist/spa /usr/share/nginx/html

# Copy nginx config and entrypoint
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]