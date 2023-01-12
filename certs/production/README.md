# These files
`montagu.vaccineimpact.org.crt` is the certicate file provided by ICT on renewal; its
original name ends with `.pem`, and the structure of the certificate with the three
parts is referred to as `pemia` when downloading it.

`certificate_description` is the result of running:

```
openssl crl2pkcs7 -nocrl -certfile montagu.vaccineimpact.org.crt \
| openssl pkcs7 -print_certs -text -noout > certificate_description
```

(See https://serverfault.com/a/755815/232668)

When updating the certificate, look at the diff in Git on this file. 

# Renewing

* Renewal is now handled yearly with an ICT request. They will email us 6 weeks before
  expiry. The reside-bot-reboot teams channel will also check the live expiry and 
  complain when there is a month to go.

* The private key is `/secret/vimc/ssl/v2/production/key`; use the instructions 
  on https://github.com/reside-ic/proxy-nginx/ to create the CSR (do not follow the instructions about writing the resulting certificate to the vault; the cert actually lives in this repo.)

* The CSR needs posting to ICT. Start at
  https://servicemgt.imperial.ac.uk/ask and choose Contact Us, search for
  `certificate` in the box at the top, and hopefully a result for 
  *Security Certificate Request* is available. 

* It is fairly self-explanatory; the certificate is a renewal, `montagu.vaccineimpact.org` is
  the FQDN, it is a *production* environment, and the CSR text needs pasting at the end.

* An additional step is needed since the FQDN is not obviously Imperial. ICT will get in 
  touch and ask for a CNAME tag to be added to the website, to verify to the certificate
  company that we own it. This will be of the form `<text1> CNAME <text2>`.

* Login to cloudflare.com (various team members have access), and on the dashboard,
  vaccineimpact.org is registered under Alex's account. Click on that, then "DNS Settings".

* Edit the existing CNAME that looks very similar to `<text1>` `<text2>` - or add a new one
  if you prefer. The settings need to be *DNS Only*, *Not Proxied*, and *TTL Auto*.

* Inform ICT when this is done, and they should be able to make the new cert.

* The cert arrives by email; choose the `pemia` version when downloading, and create
  a new PR to update the cert, and the description, as above.

* To hot-swap the cert in, login to production, and 
```
docker exec -it montagu_proxy_1 /bin/bash
cd /etc/montagu/proxy
```

* Perhaps copy the existing `certificate.pem` to a backup. Then edit `certificate.pem` 
  to contain the new certificate. (I usually use `nano` and paste the text in with putty).

* `nginx -s reload` in the container, and verify all is well by browsing to 
   https://mnontagu.vaccineimpact.org
