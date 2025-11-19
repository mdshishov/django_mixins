from media.models import Book, Movie, AudioBook


class MediaFactory:
    @staticmethod
    def get_media_class(media_type):
        creators = {
            'book': Book,
            'movie': Movie,
            'audiobook': AudioBook,
        }

        media_class = creators.get(media_type)
        if not media_class:
            raise ValueError(f"Неизвестный тип медиа: {media_type}")

        return media_class

    @staticmethod
    def create_media(media_type, **kwargs):
        media_class = MediaFactory.get_media_class(media_type)
        if not media_class:
            raise ValueError(f"Неизвестный тип медиа: {media_type}")

        return media_class.objects.create(**kwargs)
