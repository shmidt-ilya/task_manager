import csv


def write_task_to_csv(task):
    with open('tasks.csv', 'a+', newline='') as csvfile:
        fields = list(task.dict().keys())
        fields.append('task_id')
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        data = task.dict()
        if csvfile.tell() == 0:
            writer.writeheader()
            data['task_id'] = 1
        else:
            csvfile.seek(1)
            data['task_id'] = sum(1 for line in csv.reader(csvfile))
        writer.writerows([data])
    return data


def read_tasks_from_csv():
    try:
        csvfile = open('tasks.csv')
    except FileNotFoundError:
        return None
    else:
        with csvfile:
            task_list = [{k: v for k, v in row.items()}
                         for row in csv.DictReader(csvfile)]
        return task_list
