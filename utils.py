# coding:utf-8
#

# 获取经纬度
def get_lati_longi(line):
    lati = float(line.split(' ')[2])
    longi = abs(float(line.split(' ')[3]))
    return lati, longi

# 判断一个key是否在字典中
def key_in_dic(key, dic):
    if key in dic:
        return True
    else:
        return False

import calendar
import time

import datetime

class Time:
    def __init__(self,check_time):
        self._check_time = check_time

    def getDateByTime(self):
        self.myDate = []
        t = str(time.strftime('%Y-%m-'))
        for i in range(1, 32):
            timeStr = t + str(i)
            try:
                # 字符串转换为规定格式的时间
                tmp = time.strptime(timeStr, '%Y-%m-%d')
                # 判断是否为周六、周日
                if (tmp.tm_wday != 6) and (tmp.tm_wday != 5):
                    self.myDate.append(time.strftime('%Y-%m-%d', tmp))
            except:
                print('日期越界')
        if len(self.myDate) == 0:
            self.myDate.append(time.strftime('%Y-%m-%d'))
        return self.myDate

    # 把字符串转成datetime
    def string_toDatetime(self,string):
        return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

    def getDateByDateTime(self):
        self.myDate = []
        self.myDate_dict = {}
        # 获取系统时间
        # now = datetime.datetime.now()
        # 指定时间
        now_1 = self._check_time
        now = self.string_toDatetime(now_1)
        tmp = now.strftime('%Y-%m-')
        # 通过calendar获取到当月第一天的weekday，以及当月天数
        t = calendar.monthrange(now.year, now.month)
        for i in range(1, t[1]):
            dateTmp = tmp + str(i)
            myDateTmp = datetime.datetime.strptime(dateTmp, '%Y-%m-%d')
            if myDateTmp.isoweekday() != 6 and myDateTmp.isoweekday() != 7:
                self.myDate.append(myDateTmp.strftime('%Y-%m-%d'))
        if len(self.myDate) == 0:
            self.myDate.append(now.strftime('%Y-%m-%d'))
        for date in self.myDate:
            self.myDate_dict[date] = ''
        return self.myDate_dict

# weekday筛选出中午（12-15）和晚上（19-24）的签到记录
# weekend筛选出早上（8-12）和下午（15-19）的签到记录

# 判断该签到记录是否处于中午和晚上
def time_in_weekday(line):
    hour = int(line.split(' ')[1].split('T')[1].split(':')[0])
    if 12 <= hour < 15 or 19 <= hour <= 23:
        return True
    else:
        return False

# 判断该签到记录是否处于上午和下午
def time_in_weekend(line):
    hour = int(line.split(' ')[1].split('T')[1].split(':')[0])
    if 8 <= hour < 12 or 15 <= hour < 19:
        return True
    else:
        return False

# 由边获得节点
def get_nodes(line):
    new_str = line.split('\n')[0]
    new_list = new_str.split(' ')
    line_l = new_list[0]
    line_r = new_list[1]
    return line_l, line_r


# 根据节点的度，对邻接矩阵value的list中的元素进行排序,并返回度前3的节点
def related_three_node(my_lst,save_lst,my_dict):
    son_dictionary = {}
    save_dictionary = {}
    three_node = []
    i = 0
    for element in my_lst:
        son_dictionary[element] = my_dict[element]
    for sl in save_lst:
        save_dictionary[sl] = ''
    for k,v in sorted(son_dictionary.iteritems(), key=lambda asd:asd[1], reverse=True):
        if key_in_dic(k,save_dictionary):
            pass
        else:
            i += 1
            three_node.append(k)
            if i == 3:
                break
    # 但是度前3的点很有可能在之前选择的点save_node中出现过了，如果出现过了还得往下取
    return three_node

# 随机选择关联点对函数
import random
def random_nodes_pair(inputs, rate=0.7, seed=0):
    del_candidate = []
    total_length = len(inputs)
    random.seed(seed)
    # 取出输入的数据集行号到index中
    index = [i for i in range(total_length)]
    # 选出input×rate大小的数据用于删除
    del_index = random.sample(index, int(float(total_length) * rate))
    for del_i in del_index:
        del_candidate.append(inputs[del_i])
    print('del_candidate length:' + str(len(del_candidate)))
    return del_candidate

def flatten(sublist):
    my_str = ''
    count = 0
    for element in sublist:
        count += 1
        if count == len(sublist):
            my_str += str(element) + '\n'
        else:
            my_str += str(element) + ' '
    return my_str

# 记录每个用户轨迹中poi点出现的次数的字典
def count_poi(line):
    list1 = line.split()
    set1 = set(list1)
    list2 = list(set1)
    # 新建一个空的字典
    dir1 = {}

    for x in range(len(list2)):
        dir1[list2[x]] = 0  # 字典值初始为0
        for y in range(len(list1)):
            if list2[x] == list1[y]:
                dir1[list2[x]] += 1
    return dir1