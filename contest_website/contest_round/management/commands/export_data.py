import json
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder  # Import Django's JSON encoder
from contest_round.models import ContestRound, Problem

class Command(BaseCommand):
    help = 'Export data to JSON files'

    def handle(self, *args, **options):
        # Export ContestRound data
        contest_round_data = ContestRound.objects.all().values()
        for item in contest_round_data:
            item['round_duration'] = str(item['round_duration'])
        with open('contest_rounds.json', 'w') as contest_round_file:
            json.dump(list(contest_round_data), contest_round_file, indent=2, cls=DjangoJSONEncoder)

        # Export Problem data
        problem_data = Problem.objects.all().values()
        with open('problems.json', 'w') as problem_file:
            json.dump(list(problem_data), problem_file, indent=2, cls=DjangoJSONEncoder)

        self.stdout.write(self.style.SUCCESS('Data exported successfully!'))
