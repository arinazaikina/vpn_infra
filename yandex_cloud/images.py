from client import Client


class Images:

    def __init__(self) -> None:
        self.session = Client()

    def get_images(self):
        resp = self.session.get(endpoint=f'{self.session.endpoints.images}?folderId=standard-images&pageSize=1000')
        return resp

    def get_image_id(self, description: str = 'Ubuntu 22.04 OsLogin', min_disk_size: str = str(10 * 1024 ** 3)):
        images_data = self.get_images()
        min_size_image = None
        min_size = float('inf')
        for image in images_data.get('images', []):
            if image.get('description') == description and str(image.get('minDiskSize')) == min_disk_size:
                storage_size = float(image.get('storageSize', 'inf'))
                if storage_size < min_size:
                    min_size = storage_size
                    min_size_image = image
        image_id = min_size_image.get('id')
        return image_id
