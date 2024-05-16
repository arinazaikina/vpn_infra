class ApiEndpoints:
    """
    Класс, предоставляющий доступ к основным конечным точкам API облачных сервисов Яндекса.
    Включает URL-адреса для сервисов вычислений, IAM и виртуальных частных сетей.
    """

    COMPUTE_CLOUD_URLS = 'https://compute.api.cloud.yandex.net/compute/v1'
    AUTH_URLS = 'https://iam.api.cloud.yandex.net/iam/v1'
    VPS_URLS = 'https://vpc.api.cloud.yandex.net/vpc/v1'

    @property
    def auth(self):
        """Возвращает URL для получения токенов аутентификации."""
        return f'{self.AUTH_URLS}/tokens'

    @property
    def subnets(self):
        """Возвращает URL для работы с подсетями."""
        return f'{self.VPS_URLS}/subnets'

    @property
    def instances(self):
        """Возвращает URL для работы с экземплярами виртуальных машин."""
        return f'{self.COMPUTE_CLOUD_URLS}/instances'

    @property
    def instance(self):
        """Возвращает параметризованный URL для доступа к конкретному экземпляру машины."""
        return f'{self.COMPUTE_CLOUD_URLS}/instances/{{instanceId}}'

    @property
    def images(self):
        """Возвращает URL для работы с образами машин."""
        return f'{self.COMPUTE_CLOUD_URLS}/images'

    @property
    def disks(self):
        """Возвращает URL для работы с дисками."""
        return f'{self.COMPUTE_CLOUD_URLS}/disks'

    @property
    def snapshot_schedules(self):
        """Возвращает URL для работы с расписаниями создания снимков."""
        return f'{self.COMPUTE_CLOUD_URLS}/snapshotSchedules'

    @property
    def snapshot_schedule(self):
        """Возвращает параметризованный URL для доступа к конкретному расписанию создания снимков."""
        return f'{self.COMPUTE_CLOUD_URLS}/snapshotSchedules/{{snapshotScheduleId}}'
