FROM nginx:alpine

# Copy static assets and health check endpoint
COPY web/index.html /usr/share/nginx/html/index.html
COPY web/health /usr/share/nginx/html/health
COPY web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
