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
        writer.writerow(data)
    return data


def read_tasks_from_csv():
    try:
        csvfile = open('tasks.csv', 'r')
    except FileNotFoundError:
        return None
    else:
        with csvfile:
            task_list = [{k: v for k, v in row.items()}
                         for row in csv.DictReader(csvfile)]
        return None if not task_list else task_list


def read_task_from_csv(task_id, return_line_num=False):
    try:
        csvfile = open('tasks.csv', 'r')
    except FileNotFoundError:
        return None
    else:
        with csvfile:
            rows = csv.reader(csvfile)
            try:
                headers = next(rows)
            except StopIteration:
                return None
            for row in rows:
                if row[3] == str(task_id):
                    task = dict(zip(headers, row))
                    if return_line_num:
                        return rows.line_num, task
                    else:
                        return task
            else:
                return None

def update_task_in_csv(task_id, data_for_update):
    if not (found_task := read_task_from_csv(task_id, return_line_num=True)):
        return None

    rows_line_num, task = found_task
    task.update(data_for_update)

    with open('tasks.csv', 'r') as read_file:
        rows = list(csv.reader(read_file))
        rows[rows_line_num-1] = list(task.values())

    with open('tasks.csv', 'w') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(rows)

    return task
