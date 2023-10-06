# In your app's management/commands/import_data.py

import json
from django.core.management.base import BaseCommand
from datetime import timedelta  # Import timedelta
from contest_round.models import ContestRound, Problem

class Command(BaseCommand):
    help = 'Import data from JSON files'

    def handle(self, *args, **options):
        # Import ContestRound data
        with open('contest_rounds.json', 'r') as contest_round_file:
            contest_round_data = json.load(contest_round_file)
            for data in contest_round_data:
                # Convert 'round_duration' from string to timedelta
                data['round_duration'] = self.parse_duration(data['round_duration'])
                ContestRound.objects.create(**data)

        # Import Problem data
        with open('problems.json', 'r') as problem_file:
            problem_data = json.load(problem_file)
            for data in problem_data:
                Problem.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))

    def parse_duration(self, duration_str):
        parts = duration_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
