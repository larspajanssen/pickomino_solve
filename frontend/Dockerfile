FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY index.html style.css app.js api.js ./

# Configure nginx to proxy API requests to backend
COPY default.conf /etc/nginx/conf.d/default.conf
