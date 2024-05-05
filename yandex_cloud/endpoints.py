class ApiEndpoints:

    @property
    def auth(self):
        return 'https://iam.api.cloud.yandex.net/iam/v1/tokens'

    @property
    def instances(self):
        return 'https://compute.api.cloud.yandex.net/compute/v1/instances'

    @property
    def instance(self):
        return 'https://compute.api.cloud.yandex.net/compute/v1/instances/{instanceId}'

    @property
    def subnets(self):
        return 'https://vpc.api.cloud.yandex.net/vpc/v1/subnets'

    @property
    def images(self):
        return 'https://compute.api.cloud.yandex.net/compute/v1/images'
