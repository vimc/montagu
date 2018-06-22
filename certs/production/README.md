# These files
`montagu.vaccineimpact.org.crt` is the unmodified certicate file from GoDaddy.

`certificate_description` is the result of running:

```
openssl x509 -in montagu.vaccineimpact.org.crt  -noout -text > certificate_description
```

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

I ran `mv 52169ef2bf5de1c2.crt montagu.vaccineimpact.org.crt`. Given that we 
didn't have a bundle before, and given that the new certificate uses the same
CA as before, I think we don't need the bundle.
