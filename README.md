This will get you rolling:
-------------------------

1. pip3 install -r requirements.txt
1. python manage.py migrate
1. python manage.py loaddata fixtures/initial_data.json
1. STRIPE_SECRET_KEY=<stripe_testing_secret_key> python manage.py runserver

Note that you can assign any text to STRIPE_SECRET_KEY, you just won't be able to complete
a stripe purchase on the site without a valid one.


