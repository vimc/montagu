# These files
`montagu.vaccineimpact.org.crt` is the unmodified certicate file from GoDaddy.

`certificate_description` is the result of running:

```
openssl crl2pkcs7 -nocrl -certfile montagu.vaccineimpact.org.crt \
| openssl pkcs7 -print_certs -text -noout > certificate_description
```

(See https://serverfault.com/a/755815/232668)

I include it here, with the aim that next time we get a certificate we can also
update `certificate_description`, and thus get a more useful diff in Git.

# Renewing
I renewed through the GoDaddy web UI. After a few minutes wait I refreshed and
the certificate was ready for download. They offered a range of different
formats, pre-organized for different servers. I chose "other" which gave me a
zip file containing two files:

``` 
52169ef2bf5de1c2.crt
gd_bundle-g2-g1.crt
```

To combine these two files into a single certificate bundle I ran:

```
cat ~/Desktop/52169ef2bf5de1c2.crt ~/Desktop/gd_bundle-g2-g1.crt > montagu.vaccineimpact.org.crt
```
