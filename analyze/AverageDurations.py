import matplotlib.pyplot as plt
from distutils.util import strtobool

fig=plt.figure()
threshold = 1
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
        if itm["time"] > threshold and (itm["priority"] == priority or priority == -1):
            sum +=  itm["time"]
            cnt += 1

    if not cnt:
        return -1

    return sum / cnt

def average2(database, priority, lying):
    sum = 0
    cnt = 0
    for itm in database:
        if itm["time"] > threshold and (itm["priority"] == priority and itm["lying"] == lying):
            sum += itm["time"]
            cnt += 1

    if not cnt:
        return -1

    return sum / cnt

def max_time(database, priority):
    max = -1
    for itm in database:
        if itm["time"] > 0 and (itm["priority"] == priority or priority == -1):
            if itm["time"] > max:
                max = itm["time"]

    return max

def max_time2(database, priority, lying):
    max = -1
    for itm in database:
        if itm["time"] > 0 and (itm["priority"] == priority and itm["lying"] == lying):
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

    #res["max_all"] = max_time(database, -1)
    #res["max_priority"] = max_time(database, 1)
    #res["max_non_priority"] = max_time(database, 0)

    #res["max_priority_lying"] = max_time2(database, 0, 1)
    #res["max_priority_truthful"] = max_time2(database, 1, 0)

    return res


def plot_bars(data, xlabel, ylabel, title, ylimit, pos):
    plt.subplot(1, 4, pos).set_title(title.replace("-", "\n"))

    courses = list(data.keys())
    values = list(data.values())

    plt.bar(courses, values, color='maroon',
            width=0.4)
    plt.ylim(0, ylimit)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)



def plot_average(results, title, pos):
    plot_bars({'Avg': results["average_all"],
            'P': results["average_priority"],
            'NP': results["average_non_priority"],
            'TP': results["average_priority_truthful"],
            'LP': results["average_priority_lying"]},
            "", "", title, 80, pos)

'''
def plot_max(results, filename):
    plot_bars({'max': results["max_all"],
            'max\n(priority cars)': results["max_priority"],
            'max\n(non priority cars)': results["max_non_priority"],
            'max\ntruthful priority': results["max_priority_truthful"],
            'max\nlying priority': results["max_priority_lying"]},
            "Traffic type", "Max duration to reach destination", "Max duration to destination", filename, 130)
'''


suffix = ["lyingfalse-priorityfalse", "lyingfalse-prioritytrue", "lyingtrue-priorityfalse", "lyingtrue-prioritytrue"]

path = "C:/Users/vaclav/Downloads/GAMA_1.8.1_Windows_with_JDK/configuration/org.eclipse.osgi/196/0/.cp/models/Driving Skill/models/"
seed = "2.7932832505430804E18"

for i, mode in enumerate(suffix):
    filename = f"results-people-seed{seed}-{mode}.txt"
    database_baseline = load(path+filename)
    results_baseline = analyse(database_baseline)
    plot_average(results_baseline, f"{mode}", i+1)

plt.savefig(f"average-res-{seed}.png")
    #plot_max(results_baseline, f"max-{filename}.png")

'''
database = load("/Users/au674354/Desktop/gama-ethics-workspace/caesar/models/results-people-2.92-true.txt")
results = analyse(database)
print(results["average_priority_lying"])
plot_average(results, "average_2.92.png")
plot_max(results, "max_2.92.png")
'''






#C:/Users/vaclav/Downloads/GAMA_1.8.1_Windows_with_JDK/configuration/org.eclipse.osgi/196/0/.cp/models/Driving Skill/models/results-people.txt
