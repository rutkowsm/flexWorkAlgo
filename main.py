import itertools


class Employee:
    def __init__(self, name, email, personal_calendar=None, min_weekly_hours=0, max_weekly_hours=100,
                 min_shift_length=1, max_shift_length=12):
        self.name = name
        self.email = email
        self.min_weekly_hours = min_weekly_hours
        self.max_weekly_hours = max_weekly_hours
        self.min_shift_length = min_shift_length
        self.max_shift_length = max_shift_length
        self.hours_scheduled = 0  # Track the number of hours scheduled
        self.personal_calendar = [[True] * 24 for _ in range(7)]  # Initialize all hours as available

        if personal_calendar:
            for day_block in personal_calendar:
                self.set_unavailable_hours(*day_block)

    def set_unavailable_hours(self, day, start_hour, end_hour):
        """
        Block out hours in the employee's calendar when they are unavailable.
        :param day: int, the day of the week as 0=Monday, 1=Tuesday, ..., 6=Sunday
        :param start_hour: int, the starting hour to block out (inclusive)
        :param end_hour: int, the ending hour to block out (exclusive)
        """
        for hour in range(start_hour, end_hour):
            self.personal_calendar[day][hour] = False


class Vacancy:
    def __init__(self, start_time, end_time, num_vacancies=1):
        self.start_time = start_time
        self.end_time = end_time
        self.blocks = ['EMPTY'] * (end_time - start_time) * num_vacancies


class Restaurant:
    def __init__(self, name):
        self.name = name
        self.restaurant_calendar = [[] for _ in range(7)]  # 7 days in a week

    def add_vacancy(self, day, start_time, end_time):
        self.restaurant_calendar[day].append(Vacancy(start_time, end_time))


# def schedule_employees(employees, restaurant):
#     # For each day in the restaurant calendar
#     for day_index, vacancies in enumerate(restaurant.restaurant_calendar):
#         # For each vacancy in the day
#         for vacancy in vacancies:
#             # Attempt to schedule each block in the vacancy
#             for block_index in range(len(vacancy.blocks)):
#                 scheduled_employee = None
#                 for employee in employees:
#                     hour_of_day = (vacancy.start_time + block_index) % 24
#                     # Check if the employee is available and has not exceeded max weekly hours
#                     if (employee.personal_calendar[day_index][hour_of_day] and
#                             employee.hours_scheduled < employee.max_weekly_hours):
#                         # Check for min_shift_length constraint
#                         if can_schedule_shift(employee, day_index, hour_of_day, vacancy.start_time, vacancy.end_time,
#                                               block_index):
#                             vacancy.blocks[block_index] = employee.name
#                             employee.personal_calendar[day_index][hour_of_day] = False
#                             employee.hours_scheduled += 1
#                             scheduled_employee = employee
#                             break  # Stop searching if we scheduled someone
#                 # If the block remains empty after trying all employees, mark it as EMPTY
#                 if not scheduled_employee:
#                     vacancy.blocks[block_index] = 'EMPTY'
#
#     return restaurant

def schedule_employees(employees, restaurant):
    # For each day in the restaurant calendar
    for day_index, vacancies in enumerate(restaurant.restaurant_calendar):
        # For each vacancy in the day
        for vacancy in vacancies:
            # Attempt to schedule each block in the vacancy
            for employee in employees:
                # Reset available blocks for the next employee
                if can_schedule_shift(employee, day_index, vacancy.start_time, vacancy, restaurant.restaurant_calendar):
                    break  # Employee was scheduled, move to next vacancy

    return restaurant


def can_schedule_shift(employee, day_index, start_block, vacancy, restaurant_calendar):
    # Find continuous available blocks in the employee's schedule that meet the min_shift_length
    start_of_available_block = None
    for block_index in range(vacancy.start_time, vacancy.end_time):
        if employee.personal_calendar[day_index][block_index]:
            if start_of_available_block is None:
                start_of_available_block = block_index
        else:
            # If there was an ongoing available block, check if it was long enough
            if start_of_available_block is not None and block_index - start_of_available_block >= employee.min_shift_length:
                # Check if adding this shift would exceed the employee's max weekly hours
                if employee.hours_scheduled + (block_index - start_of_available_block) <= employee.max_weekly_hours:
                    # Schedule the entire shift
                    for hour in range(start_of_available_block, block_index):
                        vacancy.blocks[hour - vacancy.start_time] = employee.name
                        employee.personal_calendar[day_index][hour] = False
                    employee.hours_scheduled += (block_index - start_of_available_block)
                    return True  # Shift scheduled successfully
            # Reset the start of the available block since the employee is not available at this hour
            start_of_available_block = None

    # After checking all blocks, if there is an ongoing available block, check again if it is long enough
    if start_of_available_block is not None and vacancy.end_time - start_of_available_block >= employee.min_shift_length:
        if employee.hours_scheduled + (vacancy.end_time - start_of_available_block) <= employee.max_weekly_hours:
            for hour in range(start_of_available_block, vacancy.end_time):
                vacancy.blocks[hour - vacancy.start_time] = employee.name
                employee.personal_calendar[day_index][hour] = False
            employee.hours_scheduled += (vacancy.end_time - start_of_available_block)
            return True  # Shift scheduled successfully

    return False  # Could not find a valid shift



# Example usage:
john_calendar = [[0, 8, 11], [1, 10, 14]]  # John's busy times
kate_calendar = []  # Kate is available at all times

employee_1 = Employee(name="John", email="john@mail.com", personal_calendar=john_calendar, min_shift_length=2,
                      max_shift_length=8)
employee_2 = Employee(name="Kate", email="kate@mail.com", personal_calendar=kate_calendar, min_shift_length=4,
                      max_shift_length=10)

employees = [employee_1, employee_2]

restaurant = Restaurant("Bar Mleczny Apis")
restaurant.add_vacancy(0, 8, 16)  # Add a vacancy on Monday from 8:00 to 16:00
restaurant.add_vacancy(1, 10, 17)  # Add vacancy on Tuesday from 10:00 to 17:00
restaurant.add_vacancy(1, 12, 16)  # Add vacancy on Tuesday from 12:00 to 16:00

restaurant_schedule = schedule_employees(employees, restaurant)

# Display the schedule
for day_index, vacancies in enumerate(restaurant_schedule.restaurant_calendar):
    print(f"Day {day_index} (0=Monday, 6=Sunday):")
    for vacancy in vacancies:
        print(f"  From {vacancy.start_time} to {vacancy.end_time}: {vacancy.blocks}")
