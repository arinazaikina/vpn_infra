import time
from datetime import datetime
from typing import List

from vars import FOLDER_ID
from .client import Client


class SnapshotSchedule:
    """Класс для управления расписаниями создания снимков виртуальных дисков в облачной инфраструктуре."""

    def __init__(self) -> None:
        """Инициализирует экземпляр клиента для отправки запросов к API."""
        self.session = Client()

    def get_snapshot_schedules(self, folder_id: str = FOLDER_ID):
        """
        Получает список всех расписаний создания снимков в указанной папке.

        :param folder_id: Идентификатор папки.
        :return: Ответ API с информацией о расписаниях создания снимков.
        """
        resp = self.session.get(endpoint=f'{self.session.endpoints.snapshot_schedules}?folderId={folder_id}')
        return resp

    def get_snapshot_schedule_by_id(self, snapshot_schedule_id: str):
        """
        Получает информацию о конкретном расписании создания снимков по его идентификатору.

        :param snapshot_schedule_id: Идентификатор расписания создания снимков.
        :return: Информация о расписании создания снимков.
        """
        resp = self.session.get(
            endpoint=f'{self.session.endpoints.snapshot_schedule.format(snapshotScheduleId=snapshot_schedule_id)}')
        return resp

    def get_snapshot_schedule_by_name(self, schedule_name: str):
        """
        Получает информацию о расписании создания снимков по его имени.

        :param schedule_name: Имя расписания создания снимков.
        :return: Информация о расписании создания снимков, если найдено.
        """
        snapshot_schedules = self.get_snapshot_schedules()
        for schedule in snapshot_schedules.get('snapshotSchedules', []):
            if schedule.get('name') == schedule_name:
                return schedule
        return None

    def create_snapshot_schedule(
            self,
            name: str,
            description: str,
            disk_ids: List[str],
            schedule_expression: str = "0 0 */1 * *",
            max_snapshots_to_keep: int = 10,
            folder_id: str = FOLDER_ID) -> str:
        """
        Создает новое расписание создания снимков с указанными параметрами.

        :param name: Название расписания.
        :param description: Описание расписания.
        :param disk_ids: Список идентификаторов дисков, для которых будет создаваться снимок.
        :param schedule_expression: Крон выражение для расписания.
        :param max_snapshots_to_keep: Максимальное количество хранимых снимков.
        :param folder_id: Идентификатор папки.

        :return: Идентификатор созданного расписания создания снимков.
        """

        start_at_seconds = str(int(datetime.now().timestamp()))
        payload = {
            "name": name,
            "description": description,
            "diskIds": disk_ids,

            "schedulePolicy": {
                "expression": schedule_expression,
                "startAt": {"seconds": start_at_seconds}
            },
            "snapshotCount": max_snapshots_to_keep,
            "folderId": folder_id
        }
        resp = self.session.post(endpoint=f'{self.session.endpoints.snapshot_schedules}', json=payload)
        snapshot_schedule_id = resp.get("id")
        return snapshot_schedule_id

    def wait_for_snapshot_schedule_creating(self, snapshot_schedule_name: str, timeout=600, interval=10) -> bool:
        """
        Ожидает, пока расписание создания снимков не станет активным.

        :param snapshot_schedule_name: Имя расписания.
        :param timeout: Максимальное время ожидания в секундах.
        :param interval: Интервал между проверками состояния в секундах.

        :return: True, если расписание активировано; иначе False.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            snapshot_schedule = self.get_snapshot_schedule_by_name(snapshot_schedule_name)
            if snapshot_schedule:
                if snapshot_schedule.get('status') == 'ACTIVE':
                    print("Расписание снимков подключено.")
                    return True
            else:
                print(f"Расписание {snapshot_schedule_name} пока не создано. Ожидаем...")
                time.sleep(interval)
        print(f"Время ожидания истекло, расписание снимков не подключено.")
        return False

    def setup_snapshot_schedule(
            self,
            name: str,
            description: str,
            disk_ids: List[str],
            schedule_expression: str = "0 0 */1 * *",
            max_snapshots_to_keep: int = 10,
            folder_id: str = FOLDER_ID):
        """
        Настраивает и активирует расписание создания снимков, если оно еще не существует.

        :param name: Название расписания.
        :param description: Описание расписания.
        :param disk_ids: Список идентификаторов дисков.
        :param schedule_expression: Крон выражение для расписания.
        :param max_snapshots_to_keep: Максимальное количество хранимых снимков.
        :param folder_id: Идентификатор папки.

        :return: True, если расписание успешно создано и активировано.
        :raises Exception: Если не удалось активировать расписание.
        """
        schedule = self.get_snapshot_schedule_by_name(name)
        if schedule:
            print(f'Расписание с именем "{name}" уже существует.')
            return schedule.get('id')
        else:
            self.create_snapshot_schedule(
                name, description, disk_ids, schedule_expression, max_snapshots_to_keep, folder_id)
            is_active = self.wait_for_snapshot_schedule_creating(name)
            if is_active:
                return True
            else:
                raise Exception(f"Подключение расписания снимков не удалось.")
