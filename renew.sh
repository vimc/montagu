MONTAGU_HOSTNAME=montagu.vaccineimpact.org

certbot certonly --non-interactive \
  --server https://127.0.0.1:14000/dir \
  --keep-until-expiring \
  --agree-tos \
  --email pl2113@ic.ac.uk \
  --webroot --webroot-path=www \
  --domain ${MONTAGU_HOSTNAME}

