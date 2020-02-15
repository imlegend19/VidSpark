if __name__ == '__main__':
    with open("transcript.txt", "r") as fp:
        lines = fp.readlines()

    trans = {}
    time = None
    for x in lines:
        x = x.replace("\n", "")
        if x == "":
            continue
        elif x.split(":")[0].isdigit():
            time = x
        else:
            trans[time] = x

    with open("trans.csv", "w") as fp:
        for i in trans.items():
            i = list(i)
            i[1] = i[1].replace(',', '')
            print(i[0] + ',' + i[1], file=fp)
