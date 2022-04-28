import matplotlib.pyplot as plt
from distutils.util import strtobool
 
def load(filename):
    database = []
    f = open(filename)
    for line in f:
        line = line.strip()
        buf = line.split(' ')
        time = buf[0][len("time:"):]
        priority = buf[1][len("priority:"):]
        lying = buf[2][len("lying:"):]
        database += [{"time": int(time), "priority": int(priority), "lying": strtobool(lying)}]

    f.close()

    return database

def average(database, priority):
    sum = 0
    cnt = 0
    for itm in database:
        if itm["time"] > 1 and (itm["priority"] == priority or priority == -1):
            sum +=  itm["time"]
            cnt += 1

    if not cnt:
        return -1

    return sum / cnt

def average2(database, priority, lying):
    sum = 0
    cnt = 0
    for itm in database:
        if itm["time"] > 1 and (itm["priority"] == priority and itm["lying"] == lying):
            sum +=  itm["time"]
            cnt += 1

    if not cnt:
        return -1

    return sum / cnt

def max_time(database, priority):
    max = -1
    for itm in database:
        if itm["time"] > 1 and (itm["priority"] == priority or priority == -1):
            if itm["time"] > max:
                max = itm["time"]

    return max

def max_time2(database, priority, lying):
    max = -1
    for itm in database:
        if itm["time"] > 1 and (itm["priority"] == priority and itm["lying"] == lying):
            if itm["time"] > max:
                max = itm["time"]

    return max

def analyse(database):
    res = {}
    res["average_all"] = average(database, -1)
    res["average_priority"] = average(database, 1)
    res["average_non_priority"] = average(database, 0)

    res["average_priority_lying"] = average2(database, 0, 1)
    res["average_priority_truthful"] = average2(database, 1, 0)

    res["max_all"] = max_time(database, -1)
    res["max_priority"] = max_time(database, 1)
    res["max_non_priority"] = max_time(database, 0)

    res["max_priority_lying"] = max_time2(database, 0, 1)
    res["max_priority_truthful"] = max_time2(database, 1, 0)

    return res


def plot_bars(data, xlabel, ylabel, title, filename, ylimit):
    courses = list(data.keys())
    values = list(data.values())

    fig = plt.figure(figsize=(10, 5))

    plt.bar(courses, values, color='maroon',
            width=0.4)
    plt.ylim(0, ylimit)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename)

def plot_average(results, filename):
    plot_bars({'average': results["average_all"],
            'ave (priority cars)': results["average_priority"],
            'ave (non priority cars)': results["average_non_priority"],
            'ave truthful priority': results["average_priority_truthful"],
            'ave lying priority': results["average_priority_lying"]},
            "Traffic type", "Average duration to reach destination", "Average duration to destination", filename, 30)

def plot_max(results, filename):
    plot_bars({'max': results["max_all"],
            'max (priority cars)': results["max_priority"],
            'max (non priority cars)': results["max_non_priority"],
            'max truthful priority': results["max_priority_truthful"],
            'max lying priority': results["max_priority_lying"]},
            "Traffic type", "Max duration to reach destination", "Max duration to destination", filename, 130)


database_baseline = load("/Users/au674354/Desktop/gama-ethics-workspace/caesar/models/results-people-2.92-false.txt")
results_baseline = analyse(database_baseline)
plot_average(results_baseline, "average-baseline_2.92.png")
plot_max(results_baseline, "max-baseline_2.92.png")

database = load("/Users/au674354/Desktop/gama-ethics-workspace/caesar/models/results-people-2.92-true.txt")
results = analyse(database)
print(results["average_priority_lying"])
plot_average(results, "average_2.92.png")
plot_max(results, "max_2.92.png")




