from . import forms
from . import models
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView,View,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from book.models import Book, BorrowedBook,Comment
from book.forms import CommentForm
from django.utils import timezone
from transactions.views import send_email

# Create your views here.


class DetailPostView(DetailView):
    model = models.Book
    pk_url_kwarg = 'id'
    template_name = 'book/post_details.html'
    
    def post(self, request, *args, **kwargs):
        comment_form = forms.CommentForm(data=self.request.POST)
        book = self.get_object()
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.book = book
            new_comment.save()
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object # post model er object ekhane store korlam
        comments = book.comments.all()
        comment_form = forms.CommentForm()
        
        context['comments'] = comments
        context['comment_form'] = comment_form
        return context
    
class BookBorrowView(LoginRequiredMixin,View):
    def get(self,request,id, **kwargs):
        book = get_object_or_404(Book, id = id)
        user = self.request.user
        if user.account.balance > book.price:
            user.account.balance -= book.price
            messages.success(request, 'book borrowed successful')
            user.account.save(update_fields=['balance'])
            BorrowedBook.objects.create(
                book = book,
                user = request.user.account,
                created_on=timezone.now(),
            )
            send_email(user,book.price, 'borrow', 'Book Borrow Message','transactions/email_template.html')
            return redirect('borrow_book_lists') 
        else:
            messages.error(request, 'Insufficient balance to borrow the book')
            return redirect('homepage')

class BorrowBookListView(LoginRequiredMixin, ListView):
    model = BorrowedBook
    template_name = 'book/borrowed_book.html'
    context_object_name= 'borrowed_books'

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = BorrowedBook.objects.filter(user__user_id = user_id)
        return queryset

class BookReturnView(LoginRequiredMixin, View):
    def get(self,request,id, **kwargs):
        book = get_object_or_404(BorrowedBook, id = id)
        user = self.request.user
        user.account.balance += book.book.price
        messages.success(request, 'book return successful')
        user.account.save(update_fields=['balance'])
        send_email(user,book.book.price, 'return_book', 'Book Return Message','transactions/email_template.html')
        book.delete()
        return redirect('borrow_book_lists') 
    
    
