from django.core.management import BaseCommand, CommandError
from django.db import connection

class Command(BaseCommand):
    help = 'Use this command to create owner for this project.'

    def add_arguments(self, parser):
        return super().add_arguments(parser)

    def handle(self, *args, **options):

        cursor = connection.cursor()

        
        sql =   """
                INSERT INTO EMAIL_VERIFICATION (EMAIL_ADDRESS)
                VALUES (%s)
                """
        cursor.execute(sql, ['rabid@cycloan.com'])
        
        sql =   """
                INSERT INTO OWNER (OWNER_ID, OWNER_NAME, PASSWORD, OWNER_PHONE, EMAIL_ADDRESS, LOCATION)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

        cursor.execute(sql, [1, 'rabid', 'rabid', '01789949615', 'rabid@cycloan.com', 'Dhaka'])
"""
        try:
            cursor.execute(sql, [1, 'rabid', 'rabid'])
        except:
            raise CommandError(f'There is something wrong with the command. Run diagnostics manually.')
""" 
