from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def get_form(request):
  if request.method == "GET":
    print "Request method is GET", request.method
    return render_to_response("register_form.html",
                              context_instance=RequestContext(request))
  print "Request method is not GET", request.method

  # Process form
  first_name = request.POST["first_name"]
  last_name = request.POST["last_name"]
  email = request.POST["email"]
  phone_number = request.POST["phone_number"]
  gender = request.POST["gender"]
  birthday = request.POST["birthday"]
  experience = request.POST["experience"]
  address1 = request.POST["address1"]
  address2 = request.POST["address2"]
  address3 = request.POST["address3"]

  return render_to_response("register_form_response.html",
                            context_instance=RequestContext(request))

