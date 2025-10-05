from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.utils import timezone
from .models import Task
from .forms import TaskForm


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        # فیلترها از پارامترهای GET
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        order = self.request.GET.get('order')  # 'due' or 'priority'

        if status in ['todo', 'doing', 'done']:
            qs = qs.filter(status=status)
        if priority in ['low', 'medium', 'high']:
            qs = qs.filter(priority=priority)

        if order == 'due':
            qs = qs.order_by('due_date')
        elif order == 'priority':
            # اینجا از ordering مدل هم می‌شه استفاده کرد
            qs = qs.order_by('priority', 'due_date')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # بررسی وظایف نزدیک به سررسید برای نمایش اعلان
        now = timezone.now()
        due_soon = Task.objects.filter(notify=True).filter(due_date__isnull=False)
        due_soon = [t for t in due_soon if t.is_due_soon()]
        context['due_soon'] = due_soon
        # نگهداری انتخاب‌های فیلتر برای فرم
        context['filter_status'] = self.request.GET.get('status', '')
        context['filter_priority'] = self.request.GET.get('priority', '')
        context['order'] = self.request.GET.get('order', '')
        return context


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        messages.success(self.request, 'وظیفه با موفقیت اضافه شد.')
        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        messages.success(self.request, 'وظیفه با موفقیت بروزرسانی شد.')
        return super().form_valid(form)


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'وظیفه حذف شد.')
        return super().delete(request, *args, **kwargs)


class ToggleCompleteView(View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.status != 'done':
            task.status = 'done'
            messages.success(request, f'"{task.title}" علامت‌گذاری شد به‌عنوان انجام شده.')
        else:
            task.status = 'todo'
            messages.success(request, f'"{task.title}" به‌عنوان انجام نشده نشانه‌گذاری شد.')
        task.save()
        return redirect('tasks:list')
