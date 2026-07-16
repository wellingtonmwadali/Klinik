from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reset database by dropping all tables and clearing migration history'

    def handle(self, *args, **kwargs):
        self.stdout.write('WARNING: This will drop ALL tables in the database!')
        self.stdout.write('Make sure you are connected to the correct database.')
        
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                AND tablename NOT LIKE 'pg_%'
                AND tablename NOT LIKE 'sql_%'
            """)
            tables = cursor.fetchall()
            
            if not tables:
                self.stdout.write(self.style.WARNING('No tables found to drop.'))
                return
            
            self.stdout.write(f'Found {len(tables)} tables to drop:')
            for table in tables:
                self.stdout.write(f'  - {table[0]}')
            
            # Drop all tables
            cursor.execute('DROP SCHEMA public CASCADE;')
            cursor.execute('CREATE SCHEMA public;')
            cursor.execute('GRANT ALL ON SCHEMA public TO postgres;')
            cursor.execute('GRANT ALL ON SCHEMA public TO public;')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Database reset complete!'))
            self.stdout.write('\nRun: python manage.py migrate')
