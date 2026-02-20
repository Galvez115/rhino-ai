# ---- build stage ----
FROM node:20-alpine AS build
WORKDIR /app

# Copia solo package.json y package-lock.json (si existe)
COPY package*.json ./

# Instala dependencias
RUN npm install --no-audit --fund=false

# Copia el resto del frontend
COPY . .

# Construye Vite
RUN npm run build

# ---- serve stage ----
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]