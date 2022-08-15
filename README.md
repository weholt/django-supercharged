# django-supercharge

Supercharge is a reusable Django app meant to help development, heavy influenced by the Django Style Guide (https://github.com/HackSoftware/Django-Styleguide), by providing a few management commands:

- `startbigapp`: which creates an app according to the mentioned style guide, with `selectors.py` for ORM queries, and `services.py` for more elaborate processing and operations. All views and models are
implemented as packages instead of simple *.py files, and each model should be kept in a separate file. Views per model should also be kept in a separate file related to that model. The app will also have
its own `urls.py` file for urlpatterns, which can then be included in the global `urls.py`. It will come allready setup with a `base.html` based on Bootstrap 5, with both FontAwesome Icons 6.0 & Bootstrap Icons, HTMX and AlpineJS javascript support.

- `crud_model`: creates the base for a lot of the required files related to a model, including templates & views.

Let's show an example:


`$ python manage.py startbigapp mega_app`

This will create a new app called mega_app with all the bells and whistles described above. To add a model to that app, run:

`$ python manage.py crud_model mega_app Employee -f name:str -f age:int -f email:email -f active:bool`

This will create a new model called Employee with the following fields name, age, email & active. It will create a folder in the templates folder of mega_app, with a sub-folder called employee,
containing base templates for CRUD-operations related to that model. It will add url entries to the app-related `urls.py`, add it to the local `admin.py`. **NOTE! You'll have to add the include statement
for your apps urlpatterns in the global `urls.py` yourself at the moment**. 

Now run:

`$ python manage.py makemigrations `

`$ python manage.py migrate`

and head over to the admin to see it all in action. Now that saved you a lot of typing, ie. time. ;-)

## The Service layer aka services.py

This is a controversial topic in Django, but I agree with the Style Guide above, and think putting more elaborate queries and operations into a separate layer in the project, in our case `services.py`.

Supercharged comes with an optional implementation strategy which furthers abstracts some of the logic behind a `ServiceProcessResult`. 