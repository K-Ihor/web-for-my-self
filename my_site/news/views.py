from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView  # для создания контролеров класса
from django.urls import reverse_lazy  # для настройки редиректа для формы в виде класса
from django.contrib.auth.mixins import LoginRequiredMixin  # импортируем для скрытия ссылки add_news доб.новости(или любой другой ф-ии) тем кто не авторизован
from django.core.paginator import Paginator  # для теста постраничной навигации


from .models import News, Category
from .forms import NewsForm
from .utils import MyMixin  # для примера юзания мексина


def test(request):  # постраничная навигация (тест)
    objects = ['John1', 'paule2', 'george3', 'ringo4', 'John5', 'paule6', 'george7']
    paginator = Paginator(objects, 2)  # передаем наш список и говорим что на одной страничке нам нужно выводить 2 записи
    page_num = request.GET.get('page', 1)  # дальше получаем номер текущей странички и если этого параметра page нет то ему будет присвоена 1
    page_objects = paginator.get_page(page_num)  # передаем сюда page_num чтоб получить обьект для данной странички.
    return render(request, 'news/test.html', {'page_obj': page_objects})


class HomeNews(MyMixin, ListView):
    model = News  # будут получены вседанные из модели News для даннай странички, и нужно сразу внести правки для маршрута
    template_name = 'news/home_news_list.html'  # если мы хотим выводить свой собчтвенный шаблон то указываем его сдесь.(home_news_list - имя шаблона в темплейтс news)
    context_object_name = 'news'  # указываем название обекта с которым мы хотим работать(подозреваю что news это папка в темплейтс, запутался или приложение наше)
    # extra_context = {'title': 'Главная'}  # можем передать какие-то дополнительные данные.Опционально и желательно для статичных данных
    mixin_prop = 'hello world'  # для примера юзания мексина

    def get_context_data(self, *, object_list=None, **kwargs):  # можно юзать вместо extra_context, этот метод больше для динамических данных
        context = super().get_context_data(**kwargs)  # класс super()-вернет нам родительский метод и **kwargs передаем наш словарь
        context['title'] = self.get_upper('Главная страница')  # теперь данные которые сохранены в context нам нужно дополнить. (self.get_upper - для примера юзания мексина)
        context['mixin_prop'] = self.get_prop()  # для примера юзания мексина
        return context

    def get_queryset(self):  # чтоб получать только те данные которые нужны(будем править наш запрос)
        # обращаемся к модели и фильтруем запрос, если is_published=True то выводим новость.
        return News.objects.filter(is_published=True).select_related('category')  # select_related('category') - указываем чтоб сразу запрашивал категории(для того чтоб было меньше sql-запросов)


class NewsByCategory(MyMixin, ListView):  # Класс получения категорий
    model = News
    # template_name можно не(но мы его определим) определять так как по умолчанию он обратиться к шаблону news_list который мы сделали когда писали класс HomeNews
    template_name = 'news/home_news_list.html'  # юзаем тот же самый шаблон(не создаем новый) так как они не чем не отличаються у нас.
    context_object_name = 'news'
    allow_empty = False  # неразрешаем показ пустых списков(тем самым блокируем 500-ю ошибку, а видем 404)

    def get_context_data(self, *, object_list=None, **kwargs):  # можно юзать вместо extra_context, этот метод больше для динамических данных
        context = super().get_context_data(**kwargs)  # класс super()-вернет нам родительский метод и **kwargs передаем наш словарь
        context['title'] = self.get_upper(Category.objects.get(pk=self.kwargs['category_id']))  # получаем данные текущей категории
        return context

    def get_queryset(self):  # чтоб получать только те данные которые нужны
        # выбираем определенную категорию, которая к тому же и опубликована
        return News.objects.filter(category_id=self.kwargs['category_id'], is_published=True).select_related('category')

class ViewNews(DetailView):  #  класс для получения конкретной новости
    model = News  # указ.модель с которой будем брать инфу
    context_object_name = 'news_item'  # сонтекст данных конкретной новости будет значиться как news_item который прописан в шаблоне
    # pk_url_kwarg = 'news_id'  # указываем что путь к новости(pk_url_kwarg) будет именоваться в прописанном пути как 'news_id'
    # либо просто в пути указываем pk  и в модел.пй в def get_absolute_url тоже ставим pk  в место news_id
    # template_name = 'news/news_detail.html'  # указываем какой шаблон юзать(он юзаеться по умолчанию поэтому закоментирован)


class CreateNews(LoginRequiredMixin, CreateView):  # Класс для добавления новости(для работы с формой)
    form_class = NewsForm  # Указываем форму с которой мы будем работать
    template_name = 'news/add_news.html'  # Указываем шаблон с которым мы работаем
    # login_url = '/admin/'  # если не авторизован то будет кидать тебя по ссылке на страницу админки(или куда укажешь можно на главную 'home')
    raise_exception = True  # либо если не авторизован то возбуждать исключение 403
    # редирект (переход) на добавленную новость мы не указываем из-за того что мы раньше в моделс.пй указали
    # get_absolute_url, джанго как раз и ориентируеться на этот параметер, но мы можем его переопределить как нам нужно методом success_url
    # success_url = reverse_lazy('home')  # reverse_lazy - построет коректно ссылку и работает только тогда когда до него дойдет очередь и перейдет на главную страничку 'home'



# def index(request):  # обязательный аргумент request
#     news = News.objects.all()  # .order_by('-created_at')- выведет новости от свежей к старой.  это можно и в моделс.пй указать    #.all()  # хотим посмотреть все новости
#     # categories = Category.objects.all()  # хотим вывести категории на страничку objects.all()-указывает на то что нам нужны все категории (убрали из-за того что сделали шаблон сайтбара категории)
#     context = {
#         'news': news,
#         'title':'Список новостей',
#         # 'categories': categories, - убрали из-за того что сделали шаблон сайтбара категории
#     }
#     return render(request, 'news/index.html', context)  # передаем нашь html шаблон



    # res = '<h1>Список новостей</h1>'
    # for item in news:
    #     res += f'<div>\n<p>{item.title}</p>\n<p>{item.content}</p>\n</div>\n<hr>\n' # дописываем res следующими данными
    # # print(dir(request))  # для того чтоб показать инфу в консоле, пока что не ясную моему мозгу
    # return HttpResponse(res)  # возвращать будет http респонс(конструктор данного класса)


# def test(request):
#     return HttpResponse('<h1>Тестовая страничка</h1>')



# def get_category(request, category_id):
#     news = News.objects.filter(category_id=category_id)  # получаем определенную колонку из БД
#     # categories = Category.objects.all()  # список категорий оставляем чтоб светился в сайт-баре
#     category = Category.objects.get(pk=category_id)  # выводим инфу о запрошенной категории и получаем инф по первичному ключу pk=
#     return render(request, 'news/category.html', {'news': news, 'category': category})  # , 'categories': categories (убрали из-за того что сделали шаблон сайтбара категории)

# def view_news(request, news_id):  # получение конкретной новости
#     # news_item = News.objects.get(pk=news_id)  # сохраняем в переменную конкретную новость
#     news_item = get_object_or_404(News, pk=news_id)  # на случай если новость удалена и ссылка на нее уже не работает(обработка исключения)
#     return render(request, 'news/view_news.html', {"news_item": news_item})  # передаем, название шаблона который будет рендериться view_news.html в папке new/, и контекст {"..."}


# def add_news(request):  # Ф-я для формы добавления новости
#     if request.method == 'POST':
#         form = NewsForm(request.POST)
#         if form.is_valid():
#             # print(form.cleaned_data)
#             # для форм НЕ связанных с моделью
#             # news = News.objects.create(**form.cleaned_data)  # респаковываем наш словарь который пришел с формы методом POST и присваеваем его модели News(соханяем)
#             # для форм связанных с моделью
#             news = form.save()
#             return redirect(news)  # после сохранения, нас выводит на другую страничку (на созданную новость)
#     else:
#         form = NewsForm()  # если форму еще не заполняли то выводим просто пустую форму
#     return render(request, 'news/add_news.html', {'form': form})







