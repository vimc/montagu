import shutil

ssl = '../ssl'
artifacts = '../artifacts'
token_keypair = '../token_keypair'
certs = '../certs'
config = '../config'
orderly = "../orderly"

def delete_safely(path):
    try:
        shutil.rmtree(path)
    except:
        pass
