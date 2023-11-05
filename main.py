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
    def __init__(self, day, start_time, end_time):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.blocks = ['EMPTY'] * (end_time - start_time)


class Restaurant:
    def __init__(self, name):
        self.name = name
        self.restaurant_calendar = [[] for _ in range(7)]  # 7 days in a week

    def add_vacancy(self, day, start_time, end_time):
        self.restaurant_calendar[day].append(Vacancy(day, start_time, end_time))


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

def is_employee_available(employee, day_index, start_time, end_time):
    # Check if the employee is available for the entire duration from start_time to end_time
    return all(employee.personal_calendar[day_index][hour] for hour in range(start_time, end_time))


def find_next_available_shift(employee, day_index, vacancy):
    # Look for the next available shift within the vacancy timeframe
    for start_block in range(vacancy.start_time, vacancy.end_time):
        end_block = start_block + employee.min_shift_length
        if end_block > vacancy.end_time or employee.hours_scheduled + employee.min_shift_length > employee.max_weekly_hours:
            continue  # This shift would be out of bounds or exceed max weekly hours

        # Check if the employee is available for the entire duration of the shift
        if is_employee_available(employee, day_index, start_block, end_block):
            return start_block, end_block  # Return the valid shift times

    return None, None  # No valid shift found


def schedule_shifts_for_day(employees, day_index, vacancies):
    for vacancy in vacancies:
        employees.sort(key=lambda e: e.hours_scheduled)
        for block_index in range(len(vacancy.blocks)):
            scheduled_employee = None
            for employee in employees:
                start_time, end_time = vacancy.start_time + block_index, vacancy.start_time + block_index + 1
                if (
                    employee.hours_scheduled < employee.max_weekly_hours
                    and employee.personal_calendar[day_index][start_time]
                ):
                    vacancy.blocks[block_index] = employee.name
                    employee.personal_calendar[day_index][start_time] = False
                    employee.hours_scheduled += 1
                    scheduled_employee = employee
                    break
            # If no employee was scheduled, mark the block as 'EMPTY'
            if not scheduled_employee:
                vacancy.blocks[block_index] = 'EMPTY'


def schedule_employees(employees, restaurant):
    # First pass: fill all vacancies
    for day_index, daily_vacancies in enumerate(restaurant.restaurant_calendar):
        schedule_shifts_for_day(employees, day_index, daily_vacancies)

    # Second pass: review and redistribute for fairness
    redistribute_shifts_for_fairness(employees, restaurant)

    return restaurant


def can_schedule_employee(employee, day_index, block_index, vacancy):
    # Check if the employee is available and not exceeding max weekly hours
    start_time = vacancy.start_time + block_index
    end_time = start_time + employee.min_shift_length
    if employee.hours_scheduled >= employee.max_weekly_hours or end_time > vacancy.end_time:
        return False
    return all(employee.personal_calendar[day_index][start_time:end_time])


def schedule_employee(employee, day_index, block_index, vacancy):
    # Schedule the employee for their minimum shift length
    start_time = vacancy.start_time + block_index
    for hour in range(start_time, start_time + employee.min_shift_length):
        vacancy.blocks[hour - vacancy.start_time] = employee.name
        employee.personal_calendar[day_index][hour] = False
    employee.hours_scheduled += employee.min_shift_length


def redistribute_shifts_for_fairness(employees, restaurant):
    # Sort employees by hours scheduled (ascending)
    employees.sort(key=lambda e: e.hours_scheduled)
    # Attempt to redistribute shifts from more scheduled to less scheduled employees
    for day_index, daily_vacancies in enumerate(restaurant.restaurant_calendar):
        for vacancy in daily_vacancies:
            for block_index, block in enumerate(vacancy.blocks):
                if block == 'EMPTY':
                    continue  # Skip empty blocks
                current_employee = next((e for e in employees if e.name == block), None)
                for employee in employees:
                    if employee is current_employee:
                        continue  # Skip if it's the same employee
                    # Check if swapping is possible and beneficial for fairness
                    if can_swap_shift(current_employee, employee, day_index, block_index, vacancy):
                        swap_shift(current_employee, employee, day_index, block_index, vacancy)


def can_swap_shift(current_employee, new_employee, day_index, block_index, vacancy):
    # Check if new_employee is already scheduled for max hours
    if new_employee.hours_scheduled >= new_employee.max_weekly_hours:
        return False

    # Check if the current block plus min_shift_length for new_employee is within the vacancy limits
    if block_index + new_employee.min_shift_length > len(vacancy.blocks):
        return False

    # Check if new_employee is available for the duration of the current_employee's shift
    for hour in range(block_index, block_index + current_employee.min_shift_length):
        if hour >= len(new_employee.personal_calendar[day_index]) or not new_employee.personal_calendar[day_index][
            vacancy.start_time + hour]:
            return False

    # Check if the shift swap will not cause new_employee to exceed max_weekly_hours
    if new_employee.hours_scheduled + current_employee.min_shift_length > new_employee.max_weekly_hours:
        return False

    # If all conditions are met, we can swap the shift
    return True


def swap_shift(current_employee, new_employee, day_index, block_index, vacancy):
    # Perform the shift swap
    for hour in range(block_index, block_index + current_employee.min_shift_length):
        # Update the vacancy schedule
        vacancy.blocks[hour] = new_employee.name
        # Update the personal calendars
        current_employee.personal_calendar[day_index][vacancy.start_time + hour] = True
        new_employee.personal_calendar[day_index][vacancy.start_time + hour] = False

    # Update the hours scheduled
    current_employee.hours_scheduled -= current_employee.min_shift_length
    new_employee.hours_scheduled += current_employee.min_shift_length


# Example usage:
john_calendar = [[0, 8, 11]]  # John's busy times
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
