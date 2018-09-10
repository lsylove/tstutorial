from datetime import datetime
import re


def generate_key(id_desc):
    return id_desc[id_desc.find(": <") + 1:id_desc.find(".JavaMail") - 1].encode()


def process_email(raw_data):
    date_str = raw_data[1].split()
    date_str = date_str[2] + " " + date_str[3] + " " + date_str[4]
    date_str = datetime.strptime(date_str, "%d %b %Y").strftime("%m/%d/%Y")

    index = 4
    while raw_data[index].find("Mime-Version") == -1:
        index += 1

    raw_data = raw_data[2:index] + raw_data[index + 3:]
    raw_data = [e.split() for e in raw_data if len(e.split()) > 0]
    raw_data = [i for l in raw_data for i in l]
    raw_data = [date_str] + raw_data

    data = [""]
    for e in raw_data:
        token = e.lower().replace("-", "_")
        if "com" not in e and "www" not in e and "co." not in e and "http" not in e and "net" not in e:
            if not re.match("^[0-9:]+$", token):
                token = re.sub("[^A-Za-z0-9/'_]+", "", token)
        else:
            token = re.sub("[^A-Za-z0-9/'_.@/]+", "", token)
        if len(token) > 1 or token == "i":
            if len(token) > 6 and token[len(token) - 2:] == "20":
                token = token[len(token) - 2:]
            data.append(token)

    data2 = [""]
    count = 0
    for i, _ in enumerate(data):
        if count > 0:
            count -= 1
        elif len(data) <= i + 2:
            data2.append(data[i])
        elif re.match("^\d?$", data[i]) and re.match("^[a-z]{3}$", data[i + 1]) and re.match("^\d{4}$", data[i + 2]):
            another_date_str = data[i] + " " + data[i + 1] + " " + data[i + 2]
            another_date_str = datetime.strptime(another_date_str, "%d %b %Y").strftime("%m/%d/%Y")
            data2.append(another_date_str)
            count = 2
        elif re.match("^[a-z]{3,}$", data[i]) and re.match("^\d{2}$", data[i + 1]) and re.match("^\d{4}$", data[i + 2]):
            try:
                another_date_str = data[i] + " " + data[i + 1] + " " + data[i + 2]
                another_date_str = datetime.strptime(another_date_str, "%B %d %Y").strftime("%m/%d/%Y")
                data2.append(another_date_str)
                count = 2
            except ValueError:
                data2.append(data[i])
        else:
            data2.append(data[i])

    return data2
