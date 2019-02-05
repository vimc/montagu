from docker_helpers import docker_cp


def configure_static_server(service, keypair_paths):
    container = service.static
    print("Configuring static file server")
    docker_cp(keypair_paths['public_pem'], container.name, "/public_key.pem")
