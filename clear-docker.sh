if [[ ! $1 == "--force" ]]; then
    echo "Warning: This will stop and remove all Docker containers running on "
    echo -n "this machine. If you are sure you want to this type 'stop-montagu': "
    read input
    if [[ ! $input == "stop-montagu" ]]; then
        exit -1
    fi
fi

echo "Stopping and removing all Docker containers..."
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
exit 0