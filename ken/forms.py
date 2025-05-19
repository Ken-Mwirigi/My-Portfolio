from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True, max_length=150)
    message = forms.CharField(required=True, widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validations if needed
        return cleaned_data
