FROM nginx:1.27-alpine

COPY index.html style.css app.js api.js /usr/share/nginx/html/
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
