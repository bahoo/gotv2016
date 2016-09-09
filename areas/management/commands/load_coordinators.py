from django.core.management.base import BaseCommand, CommandError
from areas.models import WaPrecinct, Area, PrecinctCoordinator
import csv


class Command(BaseCommand):
    help = 'Load in PCO coordinators.'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='A CSV filename, with fields: precinct, full_name, email, phone_number')
        parser.add_argument('affiliation', nargs='?', type=str, default=None, choices=map(lambda a: a[0], PrecinctCoordinator.AFFILIATIONS))

    def handle(self, *args, **options):
        created_count = not_created_count = 0
        try:
            with open(options['filename'], 'rU') as file:
                reader = csv.DictReader(file)
                for line in reader:
                    # look up precinct, and clean up data dict for entry
                    precinct = WaPrecinct.objects.get(long_name=line['precinct'])
                    line['precinct_id'] = precinct.pk
                    del line['precinct']

                    line['affiliation'] = options['affiliation']
                    coordinator, created = PrecinctCoordinator.objects.get_or_create(**line)
                    if created:
                        created_count += 1
                    else:
                        not_created_count += 1
            self.stdout.write(self.style.SUCCESS('SUCCESS: Created %s coordinators (did not create %s)' % (created_count, not_created_count)))
        except IOError:
            raise CommandError("Could not open CSV file '%s'. Double-check that filename and path?" % options['filename'])