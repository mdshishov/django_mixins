# forms.py
from django import forms
from .services import MediaFactory


class MediaForm(forms.Form):
    MEDIA_TYPES = [
        ('book', 'Книга'),
        ('movie', 'Фильм'),
        ('audiobook', 'Аудиокнига'),
    ]

    media_type = forms.ChoiceField(choices=MEDIA_TYPES, label='Тип медиа')
    title = forms.CharField(max_length=200, label='Название')
    creator = forms.CharField(max_length=100, label='Автор/Режиссер')
    publication_date = forms.DateField(
        label='Дата публикации',
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    # Поля для книг
    isbn = forms.CharField(max_length=20, required=False, label='ISBN')
    page_count = forms.IntegerField(required=False, label='Количество страниц', min_value=1)

    # Поля для фильмов
    movie_duration = forms.IntegerField(required=False, label='Длительность фильма (минуты)', min_value=1)
    format = forms.CharField(max_length=10, required=False, label='Формат')

    # Поля для аудиокниг
    narrator = forms.CharField(max_length=100, required=False, label='Чтец')
    audiobook_duration = forms.IntegerField(required=False, label='Длительность аудиокниги (минуты)', min_value=1)

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')

        # Валидация в зависимости от типа медиа
        if media_type == 'book':
            if not cleaned_data.get('isbn'):
                self.add_error('isbn', 'ISBN обязателен для книг')
            if not cleaned_data.get('page_count'):
                self.add_error('page_count', 'Количество страниц обязательно для книг')

        if media_type == 'movie':
            if not cleaned_data.get('movie_duration'):
                self.add_error('movie_duration', 'Продолжительность обязательна для фильмов')
            if not cleaned_data.get('format'):
                self.add_error('format', 'Формат обязателен для фильмов')

        elif media_type == 'audiobook':
            if not cleaned_data.get('narrator'):
                self.add_error('narrator', 'Чтец обязателен для аудиокниг')
            if not cleaned_data.get('audiobook_duration'):
                self.add_error('audiobook_duration', 'Длительность обязательна для аудиокниг')

        return cleaned_data

    def save(self):
        media_type = self.cleaned_data['media_type']

        # Подготавливаем данные для фабрики
        media_data = {
            'title': self.cleaned_data['title'],
            'creator': self.cleaned_data['creator'],
            'publication_date': self.cleaned_data['publication_date'],
        }

        # Добавляем специфичные поля для каждого типа
        if media_type == 'book':
            media_data.update({
                'isbn': self.cleaned_data['isbn'],
                'page_count': self.cleaned_data['page_count']
            })
        elif media_type == 'movie':
            media_data.update({
                'duration': self.cleaned_data['movie_duration'],
                'format': self.cleaned_data['format']
            })
        elif media_type == 'audiobook':
            media_data.update({
                'duration': self.cleaned_data['audiobook_duration'],
                'narrator': self.cleaned_data['narrator']
            })

        # Используем фабрику для создания объекта
        return MediaFactory.create_media(media_type, **media_data)
