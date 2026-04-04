# Multi-stage build for optimized image size
FROM node:20-alpine AS base

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    YARN_CACHE_FOLDER=/tmp/yarn-cache

RUN apk add --no-cache libc6-compat openssl

WORKDIR /app

FROM base AS deps
ENV NODE_ENV=development

COPY package.json yarn.lock* package-lock.json* ./
RUN set -eux; \
  if [ -f yarn.lock ]; then yarn install --frozen-lockfile --non-interactive && yarn cache clean; \
  elif [ -f package-lock.json ]; then npm ci; \
  else echo "Lockfile not found." >&2; exit 1; \
  fi

FROM base AS builder
ENV NODE_ENV=development

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN SKIP_ENV_VALIDATION=true \
    NEXTAUTH_SECRET=build-placeholder \
    NEXTAUTH_URL=http://localhost:3000 \
    DATABASE_URL=file:dev.db \
    NODE_ENV=production \
    yarn build

RUN rm -rf .next/cache

FROM base AS runner

ENV NODE_ENV=production

RUN addgroup -g 1001 -S nodejs \
  && adduser -S -u 1001 nextjs -G nodejs

# public/ 目录必须存在，否则 COPY 会报错（确保 git 中有 public/.gitkeep）
RUN mkdir -p /app/public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000
ENV PORT=3000 \
    HOSTNAME=0.0.0.0

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]
