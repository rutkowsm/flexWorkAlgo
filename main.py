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

    def add_vacancy(self, day, start_time, end_time, num_vacancies=1):
        self.restaurant_calendar[day].append(Vacancy(start_time, end_time, num_vacancies))

def schedule_employees(employees, restaurant):
    for day_index, vacancies in enumerate(restaurant.restaurant_calendar):
        for vacancy in vacancies:
            for block_index, block in enumerate(vacancy.blocks):
                hour_of_day = (vacancy.start_time + block_index) % 24
                eligible_employees = [
                    emp for emp in employees if emp.personal_calendar[day_index][hour_of_day]
                                                and emp.hours_scheduled < emp.max_weekly_hours
                ]
                if eligible_employees:
                    # Sort by who has the least hours to prioritize fair scheduling
                    eligible_employees.sort(key=lambda e: e.hours_scheduled)
                    employee = eligible_employees[0]
                    vacancy.blocks[block_index] = employee.name
                    employee.personal_calendar[day_index][hour_of_day] = False
                    employee.hours_scheduled += 1

    return restaurant

# Example usage:
john_calendar = [[0, 8, 11], [1, 10, 14]]  # John's busy times
kate_calendar = []  # Kate is available at all times

employee_1 = Employee(name="John", email="john@mail.com", personal_calendar=john_calendar, min_shift_length=2,max_shift_length=8)
employee_2 = Employee(name="Kate", email="kate@mail.com", personal_calendar=kate_calendar, min_shift_length=4, max_shift_length=10)

employees = [employee_1, employee_2]

restaurant = Restaurant("Bar Mleczny Apis")
restaurant.add_vacancy(0, 8, 16, 1)  # Add a vacancy on Monday from 8:00 to 16:00
restaurant.add_vacancy(1, 10, 17, 2)  # Add two vacancies on Tuesday from 10:00 to 17:00


restaurant_schedule = schedule_employees(employees, restaurant)

# Display the schedule
for day_index, vacancies in enumerate(restaurant_schedule.restaurant_calendar):
    print(f"Day {day_index}:")
    for vacancy in vacancies:
        print(f"  From {vacancy.start_time} to {vacancy.end_time}: {vacancy.blocks}")
