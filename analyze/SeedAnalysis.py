import matplotlib.pyplot as plt
from os.path import abspath

dir = abspath("../models")
print(dir)

suffix = ["lyingfalse-priorityfalse", "lyingfalse-prioritytrue", "lyingtrue-priorityfalse", "lyingtrue-prioritytrue"]
prefix = "/results-people-seed"
max_value= 0


def load(filename):
    database = []
    f = open(filename)
    for line in f:
        line = line.strip()
        splitted = line.split(" ")
        print(line, splitted)

        res = {}
        for line_info in splitted:
            keyvalue = line_info.split(":")
            res[keyvalue[0]] = keyvalue[1]
        database += [res]

    return database

def find_max_value(database):
    maxval = -1
    for dataset in database:
        for agent in dataset:
            if int(agent["time"]) > maxval:
                maxval = int(agent["time"])
    return maxval

def draw_sublpt(agent_detail, pos):
    plt.subplot(1, 4, pos).set_title(suffix[pos-1].replace("-", "\n"))

    x = []
    y = []
    labels = []
    colors = []
    for i, agent in enumerate(agent_detail):
        x += [i]
        y += [int(agent["time"])]

        priority = ""
        if agent['priority'] == '1':
            priority = "P"

        labels += [f"{agent['agent'][len('people'):]} {priority}"]
        if agent["lying"] == "true":
            colors += ["red"]
        else:
            colors += ["gray"]

    plt.xticks(x, labels, rotation='vertical')
    ax = plt.gca()
    ax.set_ylim([0, max_value])

    bar = plt.bar(x, y, color=colors)


def draw(database, seed):

    for i, dataset in enumerate(database):
        draw_sublpt(dataset, i+1)

    plt.savefig(f"overview_seed{seed}.png")

def analyze(seed):
    global max_value
    database = []
    for suf in suffix:
        data = load(f"{dir}{prefix}{seed}-{suf}.txt")
        data.sort(key=lambda x: int(x["agent"][len("people"):]))
        database += [data]
    max_value = int(find_max_value(database) * 1.1)
    draw(database, seed)

analyze("3.2349512586278953E18")
analyze("5.5180944214829394E18")
analyze("8.8271048935955036E18")