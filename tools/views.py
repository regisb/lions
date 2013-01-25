from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms

class RegisterForm(forms.Form):
  first_name = forms.CharField(min_length=10)
  last_name = forms.CharField(max_length=50)
  email = forms.EmailField()
  phone_number = forms.CharField(max_length=20)
  gender = forms.ChoiceField(choices=[("male", "Male"), ("female", "Female")])
  birthday = forms.DateField()
  experience = forms.IntegerField()
  address1 = forms.CharField()
  address2 = forms.CharField()
  address3 = forms.CharField()

def get_form(request):
  if request.method == "GET":
    form = RegisterForm()
    return render_to_response("register_form.html",
                              {"form": form},
                              context_instance=RequestContext(request))

  # Process form
  form = RegisterForm(request.POST)
  if not form.is_valid():
    print "form is not valid", form.errors
    return render_to_response("register_form_response.html",
                              {"form": form},
                              context_instance=RequestContext(request))

  return HttpResponse("blah!")

