import csv

def write_task_to_csv(task):
    with open('tasks.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=task.dict().keys())
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerows([task.dict()])
