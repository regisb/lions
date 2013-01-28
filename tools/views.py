from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from StringIO import StringIO
import tempfile, shutil, os
import subprocess

class RegisterForm(forms.Form):
  firstname = forms.CharField(max_length=50)
  lastname = forms.CharField(max_length=50)
  email = forms.EmailField()
  mobile = forms.CharField(max_length=20)
  gender = forms.ChoiceField(choices=[("male", "Male"), ("female", "Female")])
  birthday = forms.DateField()
  experience = forms.IntegerField()
  addresslineone = forms.CharField()
  addresslinetwo = forms.CharField()
  cityandpostcode = forms.CharField()
  img = forms.FileField()

def get_form(request):
  if request.method == "GET":
    form = RegisterForm()
    return render_to_response("register_form.html",
                              {"form": form},
                              context_instance=RequestContext(request))

  # Process form
  form = RegisterForm(request.POST, request.FILES)
  if not form.is_valid():
    return render_to_response("register_form.html",
                              {"form": form},
                              context_instance=RequestContext(request))

  data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
  # Do all the processing in a temporary folder
  tempdir = tempfile.mkdtemp()

  # Save image to temporary folder
  img_name = "photo" + os.path.splitext(request.FILES["img"].name)[1]
  img_content = request.FILES["img"].read()# TODO read chunk by chunk

  img_subfolder = os.path.join(tempdir, "img")
  os.mkdir(img_subfolder)

  with open(os.path.join(img_subfolder, img_name), 'w') as img_dst:
    print "image file:", img_dst.name
    img_dst.write(img_content)
  texoptions = "\\documentclass[a4paper,12pt]{article} "
  texoptions += "\usepackage[utf8]{inputenc} "
  texoptions += "\\def\\gpath{" + img_subfolder + "/} "
  texoptions += "\\def\\photoid{"+ img_name + "} " 
  texoptions += "\\def\\datapath{"+ data_dir + "} " 

  purge_table = dict((char, None) for char in u"\\{}$&#^_%~" )
  for field in form:
    if field.name != "img":
      texoptions += "\\def\\" + field.name + "{"+ field.data.translate(purge_table) + "} "
  
  texoptions += "\\input{"+ os.path.join(data_dir, "lions.tex") + "}"
  print "tex options: ", texoptions

  # Compile
  result = subprocess.call(["pdflatex",
                            "-halt-on-error",
                            "-jobname", "lions",
                            "--output-directory=" + tempdir,
                            texoptions])
  if result == 0:
    # Return pdf file
    response = HttpResponse(open(os.path.join(tempdir, "lions.pdf")).read(),
                          content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=lions_register.pdf'
  else:
    # Return error message
    return render_to_response("register_form.html",
                              {"form": form, "error": "Sorry, there seems to be something wrong with the image you provided"},
                              context_instance=RequestContext(request))

  # Delete temporary directory
  shutil.rmtree(tempdir)
  print "directory tree deleted"

  return response
