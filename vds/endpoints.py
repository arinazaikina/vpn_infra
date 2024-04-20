class ApiEndpoints:

    @property
    def servers(self):
        return '/server'

    @property
    def server(self):
        return '/server/{server_id}'

    @property
    def ssh_keys(self):
        return '/ssh-key'

    @property
    def ssh_key(self):
        return '/ssh-key/{key_id}'
