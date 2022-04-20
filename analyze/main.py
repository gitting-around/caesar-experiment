import matplotlib.pyplot as plt

def load(filename):
    database = []
    f = open(filename)
    for line in f:
        line = line.strip()
        buf = line.split(' ')
        time = buf[0][len("time:"):]
        priority = buf[1][len("priority:"):]
        database += [{"time": int(time), "priority": int(priority)}]

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

def max_time(database, priority):
    max = -1
    for itm in database:
        if itm["time"] > 1 and (itm["priority"] == priority or priority == -1):
            if itm["time"] > max:
                max = itm["time"]

    return max


def analyse(database):
    res = {}
    res["average_all"] = average(database, -1)
    res["average_priority"] = average(database, 1)
    res["average_non_priority"] = average(database, 0)

    res["max_all"] = max_time(database, -1)
    res["max_priority"] = max_time(database, 1)
    res["max_non_priority"] = max_time(database, 0)

    return res;


def plot_bars(data, xlabel, ylabel, title, filename):
    courses = list(data.keys())
    values = list(data.values())

    fig = plt.figure(figsize=(10, 5))

    plt.bar(courses, values, color='maroon',
            width=0.4)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename)

def plot_average(results, filename):
    plot_bars({'average': results["average_all"],
            'average (priority cars)': results["average_priority"],
            'average (non priority cars)': results["average_non_priority"]},
            "Traffic type", "Average duration to reach destination", "Average duration to destination", filename)

def plot_max(results, filename):
    plot_bars({'max': results["max_all"],
            'max (priority cars)': results["max_priority"],
            'max (non priority cars)': results["max_non_priority"]},
            "Traffic type", "Max duration to reach destination", "Max duration to destination", filename)


database = load("C:/Users/vaclav/Downloads/GAMA_1.8.1_Windows_with_JDK/configuration/org.eclipse.osgi/196/0/.cp/models/Driving Skill/models/results-people.txt")
results = analyse(database)
plot_average(results, "average.png")
plot_max(results, "max.png")




