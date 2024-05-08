from vars import USER

INSTANCES_CONFIG = [
    {
        "name": "ca",
        "core_fraction": 20,
        "cores": 2,
        "memory": 1024 ** 3,
        "disk_size": 10 * 1024 ** 3,
        "os": "Ubuntu 22.04 OsLogin",
        "username": USER,
        "zone_id": "ru-central1-a",
        "platform_id": "standard-v3"
    },
    {
        "name": "vpn",
        "core_fraction": 20,
        "cores": 2,
        "memory": 1024 ** 3,
        "disk_size": 10 * 1024 ** 3,
        "os": "Ubuntu 22.04 OsLogin",
        "username": USER,
        "zone_id": "ru-central1-a",
        "platform_id": "standard-v3"
    },
    {
        "name": "monitoring",
        "core_fraction": 20,
        "cores": 2,
        "memory": 1024 ** 3,
        "disk_size": 10 * 1024 ** 3,
        "os": "Ubuntu 22.04 OsLogin",
        "username": USER,
        "zone_id": "ru-central1-a",
        "platform_id": "standard-v3"
    }
]
