import os

duplicate = [1]
while duplicate:
    reference = os.listdir("temporary_data")
    list = os.listdir("temporary_data")
    for i in range(len(list)):
        list[i] = list[i][9:15]


    duplicate = []
    for i in range(len(list)):
        if list.count(list[i]) == 1:
            continue
        else:
            duplicate.append(reference[i])

    for i in range(1, len(duplicate)):
        if duplicate[0][9:15] == duplicate[i][9:15]:
            index = duplicate.index(duplicate[i])
            if duplicate[0][0:8] > duplicate[i][0:8]:
                os.remove("temporary_data\{}".format(duplicate[i]))
            elif duplicate[0][0:8] < duplicate[i][0:8]:
                os.remove("temporary_data\{}".format(duplicate[0]))
            del duplicate[i]
            del duplicate[0]
            break
        else:
            continue


new_file = os.listdir("temporary_data")
for i in range(len(new_file)):
    new_file[i] = new_file[i][9:15]
dict = {}
for i in range(len(new_file)):
    if new_file.count(new_file[i]) == 1:
        continue
    else:
        dict[new_file[i]] = new_file.count(new_file[i])
if not dict:
    print("无须检查")
else:
    print(dict)

