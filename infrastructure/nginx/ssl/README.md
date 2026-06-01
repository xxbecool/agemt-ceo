# SSL Certificates

This directory holds TLS certificates for the Nginx reverse proxy.

## Local Development

Generate a self-signed certificate:

```bash
make ssl-self-signed
# or manually:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/C=US/ST=Dev/L=Local/O=ExecutiveAI/CN=localhost"
```

## Production

Use [Let's Encrypt](https://letsencrypt.org/) via Certbot:

```bash
certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
# Copy/symlink the certs here:
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem fullchain.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem   privkey.pem
```

> **Important**: Never commit real private keys to version control.
> This README is committed; `*.pem` files are git-ignored.
