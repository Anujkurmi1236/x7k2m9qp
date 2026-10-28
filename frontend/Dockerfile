# ---- build ----
FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

# Vite inlines this at build time, so it must be passed with --build-arg
ARG VITE_FASTAPI_BASE_URL=http://localhost:8000
ENV VITE_FASTAPI_BASE_URL=$VITE_FASTAPI_BASE_URL
RUN pnpm build

# ---- serve ----
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]