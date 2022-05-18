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
        agent = buf[3][len("agent:"):]
        database += [{"time": int(time), "priority": int(priority), "lying": strtobool(lying), "agent": agent}]

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
        return 0

    return sum / cnt

def analyse_agent(database, agent_name):
    sum = 0
    cnt = 0
    for itm in database:
        if itm["time"] > threshold and itm["agent"] == agent_name:
            sum += itm["time"]
            print (itm["agent"], itm["time"])
            cnt += 1

    if not cnt:
        return 0

    return sum / cnt

def analyse(database):
    res = {}

    res["average_all"] = average(database, -1)
    res["average_priority"] = average(database, 1)
    res["average_non_priority"] = average(database, 0)

    res["average_priority_lying"] = average2(database, 0, 1) # liars
    res["average_non_priority_non_lying"] = average2(database, 0, 0)  # liars

    return res

def analyse_agents(database):
    res = {}
    for i in range(15):

        res[f"{i}"] = analyse_agent(database, f"people{i}")
        print(f"agent{i}", analyse_agent(database, f"people{i}"))
    return res


def data_keys(data):
    keys = []
    values = []
    for itm in data:
        keys += [itm[0]]
        values += [itm[1]]

    return {"keys": keys, "values": values}



def plot_bars(data, xlabel, ylabel, title, ylimit, pos):
    plt.subplot(2, 2, pos).set_title(title)

    data_divided = data_keys(data)
    courses = data_divided["keys"]
    values = data_divided["values"]

    plt.bar(courses, values, color='maroon',
            width=0.4)
    plt.ylim(0, ylimit)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)



def plot_average(results, agents_data, title, pos):
    data = [('Avg', results["average_all"]),
              ('P', results["average_priority"]),
              ('H', results["average_non_priority_non_lying"]),
              ('L', results["average_priority_lying"])]

    for i in range(5):
        data += [(f"{i}", agents_data[f"{i}"])]

    plot_bars(data
            , "", "", title, 150, pos)

suffix = ["lyingfalse-priorityfalse", "lyingfalse-prioritytrue", "lyingtrue-priorityfalse", "lyingtrue-prioritytrue"]
#suffix = ["lyingfalse-priorityfalse"]
path = "C:/Users/vaclav/Downloads/GAMA_1.8.1_Windows_with_JDK/configuration/org.eclipse.osgi/196/0/.cp/models/Driving Skill/models/"
seed = "2.7932832505430804E18"
experiment_suffix = "nb_people5-time_to_change1000"

for i, mode in enumerate(suffix):
    filename = f"results-people-seed{seed}-{mode}.txt"
    database_baseline = load(path+filename)
    results_baseline = analyse(database_baseline)
    agents_data = analyse_agents(database_baseline)

    plot_average(results_baseline, agents_data, "", i+1)

# plt.savefig(f"average-res-{seed}-{experiment_suffix}.png")
plt.savefig(f"new_average-res-{seed}.png")
    #plot_max(results_baseline, f"max-{filename}.png")
