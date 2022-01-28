FROM node:lts-alpine@sha256:f21f35732964a96306a84a8c4b5a829f6d3a0c5163237ff4b6b8b34f8d70064b AS compiler
RUN apk add --no-cache libc6-compat
WORKDIR /frontend
COPY package*.json ./
COPY tsconfig*.json ./
RUN npm install
COPY . ./
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
RUN npm run build

FROM node:lts-alpine@sha256:f21f35732964a96306a84a8c4b5a829f6d3a0c5163237ff4b6b8b34f8d70064b AS cleanup
WORKDIR /frontend
COPY --from=compiler /frontend/.next ./.next
COPY --from=compiler /frontend/public ./public
COPY --from=compiler /frontend/package.json ./package.json
COPY --from=compiler /frontend/package-lock.json ./package-lock.json
RUN npm install --only=production

FROM node:lts-alpine@sha256:f21f35732964a96306a84a8c4b5a829f6d3a0c5163237ff4b6b8b34f8d70064b AS runner
WORKDIR /frontend
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
COPY --from=cleanup --chown=nextjs:nodejs /frontend ./
EXPOSE 3000