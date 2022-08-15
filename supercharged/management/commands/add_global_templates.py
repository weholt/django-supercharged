#!/usr/bin/env python
import os

import djclick as click

from supercharged.utils import configure_django_environ


@click.command()
def add_global_templates():

    configure_django_environ(os.getcwd())
    from django.apps import apps

    app_name = "global_templates"
    existing_app = [app for app in apps.get_app_configs() if app.name == app_name]
    if existing_app:
        raise SystemError("There is allready an app called %s" % app_name)

    frontend_path = os.path.join(os.getcwd(), app_name)
    os.makedirs(os.path.join(frontend_path, "templates"))
    open(os.path.join(frontend_path, "__init__.py"), "w").write("")
    open(os.path.join(frontend_path, "templates", "base.html"), "w").write(
        """{% extends 'base_sceleton.html' %}

{% block site_title %}The name of your site{% endblock %}

{% block page %}
<nav class="navbar navbar-expand-sm sticky-top">
  <div class="container">
      <a class="navbar-brand" href="/">Your site</a>
      <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbar1">
          <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbar1">
          <ul class="navbar-nav">
              <li class="nav-item active">
                  <a class="nav-link" href="{% url 'admin:index' %}">Admin</a>
              </li>
              <li class="nav-item">
                  <a class="nav-link" href="{% url 'admin:index' %}">Dashboard</a>
              </li>
          </ul>
          <ul class="navbar-nav ml-auto">
              <li class="nav-item active">
                  <a class="nav-link" href="#">Link</a>
              </li>
          </ul>
      </div>
  </div>
</nav>
  
<div class="container">
  <div class="row">
      <div class="col-12 py-4">
        {% block content %}
        {% endblock %}      
      </div>
  </div>
</div>  
  <!--/row-->
  <footer class="footer">
    <div class="container text-center">
      <span class="text-muted">All rights reserved - 2022 copyright Somebody / somebody@example.com</span>
    </div>
  </footer>
</div>
{% endblock %}

<!-- 

If yoy need to add any custom style or markup, inlcude more javascript etc, do this below and it will apply to all 
pages extending this template. 

-->

{% block extra_style %}
{% endblock %}

{% block extra_head %}
{% endblock %}

{% block extra_script_import %}
{% endblock %}

{% block extra_script %}
{% endblock %}
"""
    )
