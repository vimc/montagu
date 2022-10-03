ICT will send 3 files:

- `support_montagu_dide_ic_ac_uk.crt`
- `RootCertificates/QuoVadisOVIntermediateCertificate.crt`
- `RootCertificates/QuoVadisOVRootCertificate.crt`

concatenate these as

```
cat support_montagu_dide_ic_ac_uk.crt \
  RootCertificates/QuoVadisOVIntermediateCertificate.crt \
  RootCertificates/QuoVadisOVRootCertificate.crt > \
  support.montagu.crt
```

You will also have a key that should be updated in the vault

```
vault read -field=key secret/vimc/ssl/v2/support/key
vault write secret/vimc/ssl/v2/support/key key=@support.key
vault read secret/vimc/ssl/v2/support/key
```
