from django import forms

class ContactSearchForm(forms.Form):
    keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'supply chain, logistics'}),
        help_text="Comma-separated keywords"
    )
    titles = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supply Chain, Operations'}),
        help_text="Comma-separated job titles"
    )
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'chennai'}),
        initial='chennai'
    )
    max_results = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 100}),
        initial=50,
        help_text="Maximum number of results (10-100)"
    )
    per_page = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 25}),
        initial=25
    )
