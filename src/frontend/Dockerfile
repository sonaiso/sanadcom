# =============================================================================
# SICO GRC Frontend - Secure Multi-Stage Production Build
# =============================================================================
# Security improvements:
# - Multi-stage build separates build-time from runtime dependencies
# - Node.js 20 LTS (Active LTS with security patches)
# - Minimal Alpine Linux base (reduces attack surface)
# - Non-root user execution
# - Production-only dependencies in final image
# - No package managers or build tools in production
# =============================================================================

# Pin to Node.js 20 LTS Alpine for security patches and long-term support.
# Node 18 reached EOL April 2025; Node 20 LTS is supported until April 2026.
ARG NODE_VERSION=20-alpine

# -----------------------------------------------------------------------------
# Stage 1: Dependencies (cached layer for faster rebuilds)
# -----------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS deps

# Install only required system packages for node-gyp builds
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy only package files for dependency installation
COPY package*.json ./

# Install all dependencies (including devDependencies needed for build)
RUN npm ci

# -----------------------------------------------------------------------------
# Stage 2: Builder (compile application)
# -----------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source code
COPY . .

# Set production environment for optimized build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Production Runtime (minimal image)
# -----------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Create non-root user for running application
RUN addgroup --system --gid 1001 nodejs && \
  adduser --system --uid 1001 nextjs && \
  mkdir -p /app/.next && \
  chown -R nextjs:nodejs /app

# Copy built application from builder stage
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Start application
CMD ["node", "server.js"]