from django.core.management.base import BaseCommand, CommandError
from areas.models import WaPrecinct, Area, PrecinctCoordinator
import csv
import os
import records


class Command(BaseCommand):
    help = 'Load in PCO coordinators from PCO Coordinator.'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='A CSV filename, with NationBuilder\'s fields [46th Dems flavor]')
        # parser.add_argument('affiliation', nargs='?', type=str, default=None, choices=map(lambda a: a[0], PrecinctCoordinator.AFFILIATIONS))

    def handle(self, *args, **options):
        created_count = not_created_count = 0

        VoterDB = records.Database(os.environ['VOTER_REGISTRATION_DATABASE'])

        try:
            with open(options['filename'], 'rU') as file:
                reader = csv.DictReader(file)
                for line in reader:

                    try:
                        precinct = None

                        if not line['precinct_code']:
                            voters_lookup = VoterDB.query('SELECT * FROM wa_voter WHERE FName = :first_name AND LName = :last_name AND legislativedistrict = :legislative_district', first_name=line['first_name'].upper(), last_name=line['last_name'].upper(), legislative_district='46').all()
                            if len(voters_lookup) > 0:

                                index = None

                                if len(voters_lookup) == 1 and \
                                    voters_lookup[0]['regstnum'] in line['primary_address1'].upper() and \
                                    voters_lookup[0]['regstname'] in line['primary_address1'].upper():
                                    index = "1"

                                else:
                                    print ""
                                    for i, voter in enumerate(voters_lookup):
                                        print "%s: %s %s, %s %s %s %s, %s" % (i+1, voter['fname'], voter['lname'], voter['regstnum'], voter['regstpredirection'], voter['regstname'], voter['regstpostdirection'], voter['precinctcode'])
                                    print ""
                                    index = raw_input('Which voter matches %s at %s ? ' % (line['full_name'], line['primary_address1']))
                                    print ""
                                    if index == "":
                                        index = "1"

                                if index is None or index == "skip":
                                    continue
                                    
                                precinct = WaPrecinct.objects.get(long_name__contains="46-%s" % str(voters_lookup[int(index)-1]['precinctcode']).zfill(4))

                        elif len(line['precinct_code']) == 4:
                            precinct = WaPrecinct.objects.get(short_name=line['precinct_code'], long_name__contains="46-%s" % str(line['precinct_code']).zfill(4))

                        elif len(line['precinct_code']) >= 7:
                            precinct = WaPrecinct.objects.get(long_name__contains=line['precinct_code'])

                        data = {
                            'full_name': line['full_name'],
                            'email': line['email1'],
                            'phone_number': line['phone_number'],
                            'affiliation': 'delegate',
                        }

                        if "clinton" in line['tag_list'].lower():
                            notes = "Clinton"
                        elif "sanders" in line['tag_list'].lower():
                            notes = "Sanders"
                        else:
                            notes = "Precinct"
                        
                        notes += " Delegate"
                        
                        if "statedel" in line['tag_list'].lower():
                            notes += ", State Delegate"
                        elif "statealt" in line['tag_list'].lower():
                            notes += ", State Alternate"

                        data['notes'] = notes

                        if precinct:
                            data['precinct_id'] = precinct.id


                        coordinator, created = PrecinctCoordinator.objects.get_or_create(**data)
                        if created:
                            created_count += 1
                        else:
                            not_created_count += 1

                    except BaseException, e:
                        print "Barfed on %s, %s: %s" % (line['full_name'], line['primary_address1'], e.message)


            self.stdout.write(self.style.SUCCESS('SUCCESS: Created %s coordinators (did not create %s)' % (created_count, not_created_count)))
        except IOError as e:
            raise CommandError("Could not open CSV file '%s': \"%s\". Double-check that filename and path?" % (options['filename'], e))