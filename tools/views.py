# -*- coding: utf-8 -*-
# 
# copyright Régis Behmo and Alexandre Fournier, distributed under the 
# following terms:
# 
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
# 
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
# 
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
# 
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
# 
#  0. You just DO WHAT THE FUCK YOU WANT TO.

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from StringIO import StringIO
import tempfile, shutil, os
import subprocess

class Team:
  def __init__(self, gender, name, league):
    self.gender = gender
    self.name = name
    self.league = league

teams = {
    "alpha":     Team(u"Men",   u"Alpha",     u"MP"),
    "predators": Team(u"Men",   u"Predators", u"M2"),
    "east":      Team(u"Women", u"East",      u"WP"),
    "jameja":    Team(u"Women", u"Jame-Ja",   u"WP"),
    "spirit":    Team(u"Women", u"Spirit",    u"W2"),
    "beats":     Team(u"Women", u"Beats",     u"W2"),
    "cubs":      Team(u"Women", u"Cubs",      u"W2"),
    "beginners": Team(u"Mixed", u"Beginners", u"")
    }

register_teams = list((team, data.gender + " " + data.name) for team, data in teams.iteritems() )

class RegisterForm(forms.Form):
  firstname       = forms.CharField(max_length = 50)
  lastname        = forms.CharField(max_length = 50)
  email           = forms.EmailField()
  mobile          = forms.CharField(max_length = 20)
  gender          = forms.ChoiceField(choices=[("male", "Male"), ("female", "Female")])
  team            = forms.ChoiceField(choices=register_teams)
  birthday        = forms.DateField(input_formats = ['%d/%m/%Y'])
  experience      = forms.IntegerField()
  addresslineone  = forms.CharField()
  addresslinetwo  = forms.CharField(required = False)
  cityandpostcode = forms.CharField()
  img             = forms.FileField()

texoptions = ""

def addTexDef(name, definition):
  global texoptions
  texoptions += "\\def\\" + name + "{"+ definition + "} " 


def get_form(request):
  global texoptions
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
  texoptions  = "\\documentclass[a4paper,12pt]{article} "
  texoptions += "\\usepackage[utf8]{inputenc} "
  addTexDef("gpath",  img_subfolder + "/")
  addTexDef("photoid", img_name)
  addTexDef("datapath", data_dir)

  purge_table = dict((char, None) for char in "\\{}$&#^_%~")
  for field in form:
    if field.name != "img":
      if field.name == "team":
        addTexDef(field.name, teams[field.data].name.translate(purge_table))
        addTexDef("league", teams[field.data].league.translate(purge_table))
      else:
         addTexDef(field.name, field.data.translate(purge_table))

  
  texoptions += "\\input{"+ os.path.join(data_dir, "lions.tex") + "}"
  texoptions = texoptions.encode("utf-8")# encode everything in ascii. Don't ask.
  print "tex options: ", texoptions

  # Compile
  try:
    result = subprocess.Popen(["pdflatex",
                               "-halt-on-error",
                               "-jobname", "lions",
                               "--output-directory=" + tempdir,
                               texoptions],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate()[0]
    response = HttpResponse(open(os.path.join(tempdir, "lions.pdf")).read(),
                            content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=lions_register.pdf'
  except:
    print result
    response = render_to_response("register_form.html",
                                  {"form": form, "error": "Sorry, there seems to be something wrong with the image you provided"},
                                  context_instance = RequestContext(request))

  # Delete temporary directory
  shutil.rmtree(tempdir)

  return response
