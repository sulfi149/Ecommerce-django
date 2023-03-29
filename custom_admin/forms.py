from accounts.models import Account
from category.models import category
from store.models import Product,Variations
from django import forms


# Create your forms here.
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'


class CForm(forms.ModelForm):
    class Meta:
        model = category
        fields = '__all__'        

class PForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class VForm(forms.ModelForm):
    class Meta:
        model = Variations
        fields = '__all__'