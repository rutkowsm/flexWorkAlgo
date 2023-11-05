import itertools

class Employee:
    def __init__(self, name, email, min_weekly_hours=0, max_weekly_hours=100,
                 min_shift_length=1, max_shift_length=12, personal_calendar=None):
        self.name = name
        self.email = email
        self.min_weekly_hours = min_weekly_hours
        self.max_weekly_hours = max_weekly_hours
        self.min_shift_length = min_shift_length
        self.max_shift_length = max_shift_length
        # Initialize personal_calendar with True (available) if not provided
        self.personal_calendar = personal_calendar if personal_calendar else [[True] * 24 for _ in range(7)]
        self.hours_scheduled = 0  # Track the number of hours scheduled

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
            for block_index in range(len(vacancy.blocks)):
                for employee in employees:
                    # If the employee is already scheduled for the max weekly hours, skip
                    if employee.hours_scheduled >= employee.max_weekly_hours:
                        continue
                    # Check if employee is available for this hour block
                    if employee.personal_calendar[day_index][(vacancy.start_time + block_index) % 24]:
                        # Assign the employee to this block
                        vacancy.blocks[block_index] = employee.name
                        # Update the employee's personal calendar to mark this hour as busy
                        employee.personal_calendar[day_index][(vacancy.start_time + block_index) % 24] = False
                        # Increment the employee's scheduled hours
                        employee.hours_scheduled += 1
                        break  # Move on to the next block after scheduling an employee
    # Return the updated restaurant calendar
    return restaurant

# Example usage:
restaurant = Restaurant("Bar Mleczny Apis")
restaurant.add_vacancy(0, 8, 16, 1)  # Add a vacancy on Monday from 8:00 to 16:00

employees = [
    Employee("John", "john@mail.com"),
    Employee("Kate", "kate@mail.com")
]

restaurant_schedule = schedule_employees(employees, restaurant)

# Display the schedule
for day_index, vacancies in enumerate(restaurant_schedule.restaurant_calendar):
    print(f"Day {day_index}:")
    for vacancy in vacancies:
        print(f"  From {vacancy.start_time} to {vacancy.end_time}: {vacancy.blocks}")
