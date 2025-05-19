# queries/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FacialExpressionQuery


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text="Required. Inform a valid email address."
    )
    # You could add other fields here, like 'first_name', 'last_name' if needed
    # Make sure to include them in the Meta class fields list if you do

    class Meta(UserCreationForm.Meta):
        model = User  # Use Django's built-in User model
        fields = (
            "username",
            "email",
        )  # Add 'first_name', 'last_name' here if you added them above
        # If you only want email/password registration, you might need a custom form entirely


class QueryCreateForm(forms.ModelForm):
    class Meta:
        model = FacialExpressionQuery
        # Specify the fields to include in the form
        fields = ["subject_name", "uploaded_photo", "notes"]
        # You can customize widgets if needed, e.g., for styling
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),  # Make notes field a bit larger
        }
        labels = {
            "subject_name": "Subject Name",
            "uploaded_photo": "Face Photo",
            "notes": "Optional Notes",
        }
