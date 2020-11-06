from django import forms

CITY_COHICES = (
    ("1", "Balcarce"),
    ("2", "Miramar"),
    ("3", "Buenos Aires"),
    ("4", "Tandil"),
)

class cities_form(forms.Form):
    city_form = forms.MultipleChoiceField(choices=CITY_COHICES)
