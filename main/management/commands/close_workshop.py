from django.core.management.base import BaseCommand
from django.db.models import F
from django.conf import settings
import random

from main.models import Workshop, Workshop_groups, WorkshopVisitors, Workshop_designations

class Command(BaseCommand):
    help = 'Closes a workshop and assigns visitors to tables with designation priority or randomly'

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', type=int, help='ID of the workshop to close')

    def validate_workshop_capacity(self, workshop, total_visitors):
        total_table_seats = workshop.workshop_tables * workshop.workshop_seats_per_table
        if total_visitors > total_table_seats:
            self.stdout.write(self.style.WARNING(
                f'Note: Total visitors ({total_visitors}), Available seats ({total_table_seats})'
            ))
            return False
        return True

    def get_available_tables_for_presenters(self, workshop):
        if not workshop.presenter_tables:
            return []
        return [int(table.replace('T', '')) for table in workshop.presenter_tables.split(',')]

    def get_tables_for_designation(self, designation):
        if not designation.designation_tables:
            return []
        return [int(table.replace('T', '')) for table in designation.designation_tables.split(',')]

    def check_table_capacity(self, table_num, available_tables, seats_per_table):
        """
        Check if a specific table has capacity for more visitors
        """
        current_seats = available_tables.get(table_num, 0)
        return current_seats > 0 and current_seats <= seats_per_table

    def allocate_visitors_to_specific_tables(self, visitors, specific_tables, available_tables, table_group_map, seats_per_table, dry_run=False):
        remaining_visitors = list(visitors)
        allocated_visitors = []

        for table_num in specific_tables:
            if not remaining_visitors:
                break

            # Check if table exists and has capacity
            if not self.check_table_capacity(table_num, available_tables, seats_per_table):
                continue

            current_available_seats = available_tables[table_num]
            visitors_to_seat = remaining_visitors[:current_available_seats]
            table_str = f'T{table_num}'
            group_name = table_group_map.get(table_str, 'Default')

            for visitor in visitors_to_seat:
                if not dry_run:
                    visitor.alloted_table = table_str
                    visitor.alloted_group = group_name
                    visitor.save()

                    # Print allocation info
                    allocation_msg = (
                        f'Assigned Table {table_num} (Seat {seats_per_table - current_available_seats + 1}), '
                        f'Group {group_name} to {visitor.email}'
                    )
                    if visitor.designation:
                        allocation_msg += f' ({visitor.designation.designation_name})'
                    self.stdout.write(allocation_msg)

                    allocated_visitors.append(visitor)
                    available_tables[table_num] -= 1

            remaining_visitors = remaining_visitors[len(visitors_to_seat):]

        if remaining_visitors:
            self.stdout.write(self.style.WARNING(
                f'Remaining visitors unallocated: {[v.email for v in remaining_visitors]}'
            ))

        return remaining_visitors

    def handle(self, *args, **options):
        workshop_id = options['workshop_id']

        try:
            workshop = Workshop.objects.get(id=workshop_id)

            if workshop.is_closed:
                self.stdout.write(self.style.WARNING('Workshop is already closed'))
                return

            # Get workshop configuration
            seats_per_table = workshop.workshop_seats_per_table
            total_tables = workshop.workshop_tables

            # Initialize available tables with exact seat count
            available_tables = {table_num: seats_per_table for table_num in range(1, total_tables + 1)}

            # Get group mappings
            workshop_groups = Workshop_groups.objects.filter(workshop_id=workshop)
            table_group_map = {
                table.strip(): group.group_name
                for group in workshop_groups
                for table in group.tables.split(',')
            }

            self.stdout.write('\n=== Workshop Allocation Preview ===\n')
            self.stdout.write(f'Seats per table: {seats_per_table}\n')

            # Handle presenters first
            presenters = WorkshopVisitors.objects.filter(
                workshop_id=workshop,
                is_presenter=True
            ).order_by('designation__designation_name')

            if presenters:
                self.stdout.write('\n>>> Presenter Allocations:')
                presenter_tables = self.get_available_tables_for_presenters(workshop)
                if not presenter_tables:
                    self.stdout.write('No specific presenter tables defined')
                unallocated_presenters = self.allocate_visitors_to_specific_tables(
                    presenters,
                    presenter_tables,
                    available_tables,
                    table_group_map,
                    seats_per_table
                )

            # Handle designation-based allocation
            if workshop.is_designation_required:
                designations = Workshop_designations.objects.filter(
                    workshop_id=workshop
                ).order_by('id')

                for designation in designations:
                    designation_visitors = WorkshopVisitors.objects.filter(
                        workshop_id=workshop,
                        is_presenter=False,
                        designation=designation,
                        alloted_table__isnull=True
                    )

                    if designation_visitors:
                        self.stdout.write(f'\n>>> {designation.designation_name} Allocations:')
                        designation_tables = self.get_tables_for_designation(designation)
                        if not designation_tables:
                            self.stdout.write(f'No specific tables defined for {designation.designation_name}')
                        self.allocate_visitors_to_specific_tables(
                            designation_visitors,
                            designation_tables,
                            available_tables,
                            table_group_map,
                            seats_per_table
                        )
            else:
                # Random allocation for remaining visitors, prioritizing group allocation
                remaining_visitors = WorkshopVisitors.objects.filter(
                    workshop_id=workshop,
                    alloted_table__isnull=True
                )

                if remaining_visitors:
                    self.stdout.write('\n>>> Table Allocations:')
                    
                    # Get presenter tables from workshop configuration
                    presenter_tables = {int(table.strip('T')) for table in workshop.presenter_tables.split(',')} if workshop.presenter_tables else set()

                    for visitor in remaining_visitors:
                        if visitor.is_presenter:
                            # For presenters, only allow tables defined in workshop.presenter_tables
                            valid_tables = presenter_tables
                        else:
                            # For regular visitors, get all tables except presenter tables
                            valid_tables = {int(table.strip('T')) for table in table_group_map.keys() if int(table.strip('T')) not in presenter_tables}
                        
                        # Filter available tables based on visitor type
                        filtered_available_tables = {
                            table: seats 
                            for table, seats in available_tables.items()
                            if table in valid_tables
                        }

                        available_tables_list = [
                            (table, seats)
                            for table, seats in filtered_available_tables.items()
                            if self.check_table_capacity(table, available_tables, seats_per_table)
                        ]
                        
                        if not available_tables_list:
                            visitor_type = "presenter" if visitor.is_presenter else "regular"
                            self.stdout.write(self.style.WARNING(f'No more available seats for {visitor_type}'))
                            continue
                        
                        # Randomly select a table with available seats
                        table_num, seats = random.choice(available_tables_list)
                        table_str = f'T{table_num}'
                        group_name = table_group_map[table_str]
                        
                        visitor.alloted_table = table_str
                        visitor.alloted_group = group_name
                        visitor.save()
                        
                        current_seat = seats_per_table - available_tables[table_num] + 1
                        visitor_type = "Presenter" if visitor.is_presenter else "Visitor"
                        self.stdout.write(
                            f'Assigned {visitor_type} to Table {table_num} (Seat {current_seat}), '
                            f'Group {group_name}: {visitor.email}'
                        )
                        
                        available_tables[table_num] -= 1

                        if available_tables[table_num] == 0:
                            available_tables_list = [
                                (t, s) for t, s in available_tables.items()
                                if self.check_table_capacity(t, available_tables, seats_per_table)
                            ]

            # Show final table capacity summary
            self.stdout.write('\n=== Table Capacity Summary ===')
            for table_num, seats in available_tables.items():
                group = table_group_map.get(f'T{table_num}', 'Default')
                status = "Available" if seats > 0 else "Full"
                self.stdout.write(
                    f'Table {table_num} (Group {group}): '
                    f'{seats}/{seats_per_table} seats remaining ({status})'
                )

            # Close the workshop after allocation
            workshop.is_closed = True
            workshop.save()

            self.stdout.write(self.style.SUCCESS('Workshop closed successfully'))

        except Workshop.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Workshop with ID {workshop_id} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Preview generation issue: {str(e)}'))
