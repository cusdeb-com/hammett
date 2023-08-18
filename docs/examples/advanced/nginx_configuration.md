```
server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate cert.pem;
    ssl_certificate_key private.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```
