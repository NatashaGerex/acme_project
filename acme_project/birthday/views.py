from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
# from django.core.paginator import Paginator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import BirthdayForm, CongratulationForm
from .utils import calculate_birthday_countdown
from .models import Birthday, Congratulation


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class BirthdayCreateViews(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BirthdayUpdateView(UpdateView):
    model = Birthday
    form_class = BirthdayForm


class BirthdayDeleteViews(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayListView(ListView):
    model = Birthday
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    ordering = 'first_name'
    paginate_by = 4


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        context['form'] = CongratulationForm()
        context['congratulations'] = (
            self.object.congratulations.select_related('author')
        )
        return context


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')

@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk)



# def birthday(request, pk=None):
#     if pk is not None:
#         instance = get_object_or_404(Birthday, pk=pk)
#     else:
#         instance = None
#     form = BirthdayForm(
#         request.POST or None,
#         files=request.FILES or None,
#         instance=instance
#     )
#     context = {'form': form}
#     if form.is_valid():
#         form.save()
#         birthday_countdown = calculate_birthday_countdown(
#             form.cleaned_data['birthday']
#         )
#         context.update({'birthday_countdown': birthday_countdown})
#     return render(request, 'birthday/birthday.html', context)


# def birthday_list(request):
#     birthdays = Birthday.objects.order_by('id')
#     paginator = Paginator(birthdays, 4)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     # context = {'birthdays': birthdays}
#     context = {'page_obj': page_obj}
#     return render(request, 'birthday/birthday_list.html', context)


# def delete_birthday(request, pk):
#     instance = get_object_or_404(Birthday, pk=pk)
#     form = BirthdayForm(instance=instance)
#     context = {'form': form}
#     if request.method == 'POST':
#         instance.delete()
#         return redirect('birthday:list')
#     return render(request, 'birthday/birthday.html', context)
