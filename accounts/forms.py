from typing import Any
from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import UserAccount,UserAddress
from accounts.constants import GENDER_TYPE

class UserRegistrationForm(UserCreationForm):
    age = forms.IntegerField()
    gender = forms.ChoiceField(choices = GENDER_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    street_name = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2','age', 'gender', 'birth_date', 'street_name', 'city', 'postal_code', 'country']

    def save(self,commit=True):
        new_user = super().save(commit=False)
        if commit == True:
            new_user.save()
            age = self.cleaned_data.get('age')
            gender = self.cleaned_data.get('gender')
            birth_date = self.cleaned_data.get('birth_date')
            street_name = self.cleaned_data.get('street_name')
            city = self.cleaned_data.get('city')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')

            user_account, created = UserAccount.objects.get_or_create(
                user=new_user,
                defaults={
                    'account_no': 10000 + new_user.id,
                    'age': age,
                    'gender': gender,
                    'birth_date': birth_date
                }
            )

            user_address, created = UserAddress.objects.get_or_create(
                user=new_user,
                defaults={
                    'street_name': street_name,
                    'postal_code': postal_code,
                    'city': city,
                    'country': country
                }
            )

        return new_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })


class SignupForm(UserCreationForm):
    # account_type = forms.ChoiceField(choices=UserAccount.ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # account_type = self.cleaned_data.get('account_type')

            UserAccount.objects.create(
                user=user,
                # account_type=account_type,
            )
        return user

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({     
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                ) 
            })



class UserUpdateForm(forms.ModelForm):
    age = forms.IntegerField()
    gender = forms.ChoiceField(choices = GENDER_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    street_name = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['gender'].initial = user_account.gender
                self.fields['age'].initial = user_account.age
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_name'].initial = user_address.street_name
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account,create = UserAccount.objects.get_or_create(user=user)
            user_address, create = UserAddress.objects.get_or_create(user=user)

            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.gender = self.cleaned_data['gender']
            user_account.age = self.cleaned_data['age']
            user_account.save()

            user_address.street_name = self.cleaned_data['street_name']
            user_address.city = self.cleaned_data['city']
            user_address.country = self.cleaned_data['country']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.save()

        return user