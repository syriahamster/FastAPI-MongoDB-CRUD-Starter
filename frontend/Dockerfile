# Use the official Nginx image (alpine version for a small footprint)
FROM nginx:alpine

# Remove the default configuration provided by Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx configuration file
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy our static HTML file into the appropriate directory
COPY index.html /usr/share/nginx/html/index.html