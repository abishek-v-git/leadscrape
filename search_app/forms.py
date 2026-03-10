from django import forms

class ContactSearchForm(forms.Form):
    keywords = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'supply chain, logistics'}),
        help_text="Keywords (e.g. SaaS, Fintech)"
    )
    titles = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEO, CTO, Owner'}),
        help_text="Job titles (comma separated)"
    )
    seniorities = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'c_suite, vp, director'}),
        help_text="e.g. c_suite, vp, director, manager, founder"
    )
    industries = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Software, Real Estate'}),
        help_text="Industries (comma separated)"
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'United States, Chennai'}),
        initial='United States'
    )
    company_size = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1-10, 11-50, 51-200'}),
        help_text="Ranges: 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+"
    )
    max_results = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 500}),
        initial=50,
        help_text="Max leads to pull (10-500)"
    )
    per_page = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 100}),
        initial=50
    )
