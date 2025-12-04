import os
import time
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Resetuje databázi, smaže obrázky a nahraje data'

    def handle(self, *args, **kwargs):
        print("Čekám 5 sekund...")
        time.sleep(5)

        print("Mažu a resetuji databázi...")
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')

        auction_images_path = 'media/auction_images/photos_add_auction'
        if os.path.exists(auction_images_path):
            shutil.rmtree(auction_images_path)
            os.makedirs(auction_images_path)

        call_command('makemigrations')
        call_command('migrate')
        call_command('loaddata', 'initial_data.json')
        call_command('populate_date')

        print("Hotovo.")
