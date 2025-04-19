FROM nginx:1.25-alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx config
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Create directory for Let's Encrypt certificates
RUN mkdir -p /var/www/certbot

# Create directory for Nginx cache
RUN mkdir -p /var/cache/nginx

# Set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/www/certbot

# Expose ports
EXPOSE 80 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]