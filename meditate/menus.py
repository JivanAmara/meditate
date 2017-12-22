from menu import Menu, MenuItem
from django.shortcuts import reverse
from meditate.views import (
    homepage, about_author, sample, why_meditate, buy_book, subscribe_mentoring
)

Menu.add_item("main", MenuItem("Home", reverse(homepage), weight=10))
Menu.add_item("main", MenuItem("About the Author", reverse(about_author), weight=20))
Menu.add_item("main", MenuItem("Sample from Book", reverse(sample), weight=30))
Menu.add_item("main", MenuItem("Why Meditate", reverse(why_meditate), weight=40))
Menu.add_item("main", MenuItem("Buy Book", reverse(buy_book), weight=50))
Menu.add_item("main", MenuItem("Subscribe to Mentoring", reverse(subscribe_mentoring), weight=60))
