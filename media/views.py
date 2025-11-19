# views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView

from .forms import MediaForm
from .models import Book, Movie, AudioBook
from .services import MediaFactory


class MediaListView(ListView):
    template_name = 'media_library/media_list.html'
    context_object_name = 'media_items'

    def get_queryset(self):
        books = list(Book.objects.all())
        movies = list(Movie.objects.all())
        audiobooks = list(AudioBook.objects.all())
        return books + movies + audiobooks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Группируем по типам для отображения
        context['books'] = Book.objects.all()
        context['movies'] = Movie.objects.all()
        context['audiobooks'] = AudioBook.objects.all()
        return context


class MediaDetailView(DetailView):
    template_name = 'media_library/media_detail.html'
    context_object_name = 'media_item'

    def get_object(self):

        pk = self.kwargs.get('pk')
        media_type = self.kwargs.get('media_type')
        media_class = MediaFactory.get_media_class(media_type)

        return media_class.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_item = self.object

        # Определяем доступные действия на основе типа объекта и миксинов
        context['available_actions'] = self.get_available_actions(media_item)
        context['media_type'] = self.get_media_type(media_item)

        return context

    def get_available_actions(self, media_item):
        actions = []

        # Базовые действия
        actions.append(('describe', 'Описание', 'btn-primary'))

        # Действия в зависимости от типа и миксинов
        if hasattr(media_item, 'read_sample'):
            actions.append(('read', 'Читать отрывок', 'btn-info'))

        if hasattr(media_item, 'play_trailer'):
            actions.append(('play_trailer', 'Смотреть трейлер', 'btn-warning'))

        if hasattr(media_item, 'borrow') and not media_item.is_borrowed:
            actions.append(('borrow', 'Взять в аренду', 'btn-success'))

        if hasattr(media_item, 'download'):
            actions.append(('download', 'Скачать', 'btn-secondary'))

        return actions

    def get_media_type(self, media_item):
        if isinstance(media_item, Book):
            return 'book'
        elif isinstance(media_item, Movie):
            return 'movie'
        elif isinstance(media_item, AudioBook):
            return 'audiobook'
        return 'unknown'


class MediaCreateView(TemplateView):
    template_name = 'media_library/media_form.html'

    def get(self, request, *args, **kwargs):
        form = MediaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = MediaForm(request.POST)
        if form.is_valid():
            # Используем фабрику через форму
            form.save()
            return redirect('media_library:media_list')
        return render(request, self.template_name, {'form': form})


def media_action(request, media_type, item_id):
    # Используем фабрику для получения класса медиа
    media_class = MediaFactory.get_media_class(media_type)
    if not media_class:
        return JsonResponse({'error': 'Неизвестный тип медиа'}, status=400)

    # Диспетчеризация через словарь
    action_handlers = {
        'book': {
            'describe': lambda obj: obj.get_description(),
            'read': lambda obj: obj.read_sample(),
            'borrow': lambda obj: obj.borrow(request.user.username if request.user.is_authenticated else 'Гость'),
            'download': lambda obj: "Книги недоступны для скачивания",
        },
        'movie': {
            'describe': lambda obj: obj.get_description(),
            'play_trailer': lambda obj: obj.play_trailer(),
            'download': lambda obj: obj.download(),
        },
        'audiobook': {
            'describe': lambda obj: obj.get_description(),
            'download': lambda obj: obj.download(),
            'borrow': lambda obj: obj.borrow(request.user.username if request.user.is_authenticated else 'Гость'),
            'play_trailer': lambda obj: "Аудиокниги не имеют трейлеров",
        }
    }

    action = request.POST.get('action', 'describe')

    # Получаем обработчик действия
    handler_dict = action_handlers.get(media_type, {})
    handler = handler_dict.get(action)
    if not handler:
        return JsonResponse({'error': 'Неизвестное действие'}, status=400)

    # Получаем объект и выполняем действие
    try:
        item = media_class.objects.get(id=item_id)
        result = handler(item)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'result': result})
        else:
            return redirect('media_library:media_detail', pk=item_id)

    except media_class.DoesNotExist:
        return JsonResponse({'error': 'Объект не найден'}, status=404)


def borrow_media(request, media_type, pk):
    media_class = MediaFactory.get_media_class(media_type)
    try:
        item = media_class.objects.get(pk=pk)
        if hasattr(item, 'borrow'):
            result = item.borrow(request.user.username if request.user.is_authenticated else 'Гость')
            return JsonResponse({'result': result})
        else:
            return JsonResponse({'error': 'Невозможно взять в аренду'}, status=400)

    except media_class.DoesNotExist:
        return JsonResponse({'error': 'Объект не найден'}, status=404)


def download_media(request, media_type, pk):
    media_class = MediaFactory.get_media_class(media_type)
    try:
        item = media_class.objects.get(pk=pk)
        if hasattr(item, 'download'):
            result = item.download()
            return JsonResponse({'result': result})
        else:
            return JsonResponse({'error': 'Невозможно скачать'}, status=400)

    except media_class.DoesNotExist:
        return JsonResponse({'error': 'Объект не найден'}, status=404)
