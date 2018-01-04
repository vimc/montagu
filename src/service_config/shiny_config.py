from docker_helpers import docker_cp
def configure_shiny_proxy(service, keypair_paths):
    container = service.shiny_proxy
    print("Configuring shiny proxy API")
    docker_cp(keypair_paths['public_pem'], container.name,
              "/public_key.pem")
