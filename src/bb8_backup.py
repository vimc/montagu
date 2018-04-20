from subprocess import run

targets = ["orderly"]
finished_setup = False
bb8_dir = "../montagu-bb8/bb8"


def requires_bb8_setup(func):
    def decorated(*args, **kwargs):
        global finished_setup
        if not finished_setup:
            setup()
        return func(*args, **kwargs)
    return decorated


def setup():
    global finished_setup
    print("- Configuring and installing bb8 backup service with these "
          f"targets: {targets}")
    args = ["./setup.sh", "../config.json"] + targets
    run(args, cwd=bb8_dir, check=True)
    finished_setup = True


@requires_bb8_setup
def backup():
    print("Performing bb8 backup")
    run(["bb8", "backup"], check=True)


@requires_bb8_setup
def schedule():
    print("Scheduling bb8 backup")
    run("./schedule", cwd=bb8_dir, check=True)


@requires_bb8_setup
def restore():
    print("Restoring from remote bb8 backup")
    run(["bb8", "restore"], check=True)
