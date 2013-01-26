from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from StringIO import StringIO
import tempfile, shutil, os

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
    return render_to_response("register_form_response.html",
                              {"form": form},
                              context_instance=RequestContext(request))

  data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
  # Do all the processing in a temporary folder
  tempdir = tempfile.mkdtemp()
  print "doing everything in", tempdir
  # Save image to temporary file
  img_name = request.FILES["img"].name
  img_content = request.FILES["img"].read()# TODO read chunk by chunk
  img_orig = tempfile.NamedTemporaryFile(dir=tempdir, delete=False)
  print "temp image file:", img_orig.name
  img_orig.write(img_content)
  img_orig.flush()
  # Convert image to png format
  img_dst = os.path.join(tempdir, "photo.png")
  os.system("convert %s %s" % (img_orig.name, img_dst))
  # Load tex data and process it
  data_src = os.path.join(data_dir, "lions.tex")
  with open(data_src) as f:
    data = f.read()
    for field in form:
      if field.name != "img":
        data = data.replace("\\" + field.name, field.data)
      else:
        data = data.replace("\\photoid", "photo.png")
    tex_dst = os.path.join(tempdir, "lions.tex")
    # Write tex data to temp file
    with open(tex_dst, "w") as tex_file:
      tex_file.write(data)
  # Copy lvb.png and lions.png image
  shutil.copy(os.path.join(data_dir, "lions.png"), os.path.join(tempdir, "lions.png"))
  shutil.copy(os.path.join(data_dir, "lvb.png"), os.path.join(tempdir, "lvb.png"))
  # Compile
  os.system("cd %s && pdflatex -halt-on-error lions.tex" % tempdir)
  
  # Return pdf file
  response = HttpResponse(open(os.path.join(tempdir, "lions.pdf")).read(),
                          content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename=lions_register.pdf'

  # Delete temporary directory
  shutil.rmtree(tempdir)
  print "directory tree deleted"

  return response
