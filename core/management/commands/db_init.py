from django.core.management import BaseCommand, CommandError
from django.db import connection

class Command(BaseCommand):
    help = 'Use this command to init the database for this project/.'

    def add_arguments(self, parser):
        return super().add_arguments(parser)

    def handle(self, *args, **options):

        cursor = connection.cursor()
        schema_file = open('schema.sql', 'r')
        sql = schema_file.readlines()

        try:
            cursor.execute(sql)
        except:
            raise CommandError(f'There is something wrong with the command. Run diagnostics manually.')
        
        print("Table create complete!\n")