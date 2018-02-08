# coding:utf-8
import gc
import random

import utils

BK_file = '../data/subgraph_positive.txt'
BK_edges = '../data/edges_undirected1.txt' #有01就没有10
nodes_file = '../data/vec_1.txt'#得到向量表示
sorted_nodes = '../data/sorted_nodes1.txt'#获得网络中所有点（有序）
nodes_pair = '../data/nodes_pair.txt'#网络中所有点中无关联的点对（有01就没有10）
nodes_degree = '../data/nodes_degree1.txt'#网络中各点的度
train = '../data/train_undirected.txt'#网络中有关联的4223个点对作为训练集正样本（有01就没有10）
test = '../data/test_undirected.txt'#网络中无关联的1055个点对作为测试集正样本（有01就没有10）
train_new = '../data/train_double.txt'#网络中有关联的8446个点对作为训练集正样本（有01也有10）
test_ne = '../data/test_negative.txt'#nodes_pair中随机选1055个点对作为测试集负样本（有01就没有10）
train_ne = '../data/train_negative.txt'#nodes_pair中随机选4223个点对作为训练集负样本（有01就没有10）

# 通过embedding的方式获取全部节点
from gensim.models import word2vec

sentence = word2vec.LineSentence('../data/subgraph_positive.txt')
model = word2vec.Word2Vec(sentence, size=5, min_count=0, workers=15)
model.wv.save_word2vec_format('../data/vec_1.txt')


# 将所有的节点按其编号从小到大排序
nodes = []
f = open(nodes_file)
next(f)
for line in f:
    nodes.append(int(line.split(' ')[0]))
f.close()
nodes = sorted(nodes)

fs = open(sorted_nodes, 'w')
for node in nodes:
    fs.write(str(node) + '\n')
fs.close()

#
# 将BK_file中有关联的点对存入字典。其关联点对作为key(key中是有关联的点对)，value为‘0’，使用字典可以加速查找速度
dictionary = {}
total_len = 0
f = open(BK_file)
for line in f.readlines():
    total_len += 1
    if line.split('\n')[0] in dictionary.keys():
        print 'ok'
    dictionary[line.split('\n')[0]] = '0'
f.close()

# 由于BK_file中的点对有重复的（双向：如1 0;0 1）这种应该视为一个有关联的点对，所以需要查找字典
# 当查找BK_file中的1 0时，将key为1 0和0 1的value都置为1,并将点对写入edges_undirected中
# 接下来查找0 1,若key的value为1,则跳过它。这样edges_undirected中的点对就只有1 0而没有0 1了
fe = open(BK_edges, 'w')
ff = open(BK_file)
for line in ff.readlines():
    if dictionary[line.split('\n')[0]] == '0':
        fe.write(line)
        dictionary[line.split('\n')[0]] = '1'
        line_l, line_r = utils.get_nodes(line)
        new_line = line_r + ' ' + line_l
        dictionary[new_line] = '1'
    else:
        pass
fe.close()
ff.close()

# 计算社交关系拓扑图中所有节点的度
# 先根据节点文件创建节点字典，字典中所有key的初始值为0
# 遍历整个edges_undirected,每出现一个字符，就更新该字符所对应字典key的value值，将value+1
#
# 初始化dictionary_node字典
fs = open(sorted_nodes)
dictionary_node = {}
for line in fs.readlines():
    dictionary_node[line.split('\n')[0]] = '0'

# 根据BK_edges确定node的度，根据key更新字典的value
fe = open(BK_edges)
for line in fe.readlines():
    line_l, line_r = utils.get_nodes(line)
    assert dictionary_node.has_key(line_l)
    my_str_l = dictionary_node[line_l]
    dictionary_node[line_l] = str(int(my_str_l) + 1)
    assert dictionary_node.has_key(line_r)
    my_str_r = dictionary_node[line_r]
    dictionary_node[line_r] = str(int(my_str_r) + 1)
fe.close()

# 将更新的字典写入nodes_degree中
fn = open(nodes_degree, 'w')
for key in dictionary_node.keys():
    value = dictionary_node.get(key)
    node_degree = key + ' ' + value + '\n'
    fn.write(node_degree)
fn.close()

# 删除20%的点对做测试集，余下的点对做训练集

# 各节点的度构成的字典
dictionary_node = {}
fn = open(nodes_degree)
for line in fn.readlines():
    node, degree = utils.get_nodes(line)
    dictionary_node[node] = degree
fn.close()

# 从edges_undirected.txt中随机选择出30%关联点对
inputs = []
fe = open(BK_edges)
for line in fe.readlines():
    inputs.append(line.split('\n')[0])
fe.close()

del_candidate = utils.random_nodes_pair(inputs)

# 遍历要删除关联点对的候选列表del_candidate，查节点的度的字典dictionary_node
# 只有删除候选列表中关联点对的两个节点的度的值都大于1时，将该点对放入删除点对列表中del_lst
# 同时这两个节点的度分别减1,更新dictionary_node节点度字典的值
del_lst = []
count = 0
# total_len是总的关联条数（既有01又有10），所以total_len*0.1表示选出了20%的边作为测试集
test_len = int(total_len * 0.1)
for del_c in del_candidate:
    node_l, node_r = utils.get_nodes(del_c)
    if int(dictionary_node[node_l]) > 1 and int(dictionary_node[node_r]) > 1:
        del_lst.append(del_c)
        dictionary_node[node_l] = str(int(dictionary_node[node_l]) - 1)
        dictionary_node[node_r] = str(int(dictionary_node[node_r]) - 1)
        count += 1
        if count == test_len:
            break

# 再次打开原始的点对文件edges_undirected，将不再del_lst中的点写入train_undirected文件
# 将del_lst中的点对写入test_undirected文件
dictionary_test = {}
f_te = open(test, 'w')
test_ne_len = 0
for del_i in del_lst:
    test_ne_len += 1
    dictionary_test[del_i] = '0'
    f_te.write(del_i + '\n')
f_te.close()

fe = open(BK_edges)
f_tr = open(train, 'w')
train_ne_len = 0
for line in fe.readlines():
    if dictionary_test.has_key(line.split('\n')[0]):
        pass
    else:
        f_tr.write(line)
        train_ne_len += 1
f_tr.close()
fe.close()
#
# # 根据训练集train_undirected生成有向的点对，即原来只有01就没有10,现在要有01就有10
f_tr_new = open(train_new, 'w')
f_tr = open(train)
for line in f_tr.readlines():
    node_l, node_r = utils.get_nodes(line)
    f_tr_new.write(line)
    f_tr_new.write(node_r + ' ' + node_l + '\n')
f_tr.close()
f_tr_new.close()

# 由于计算auc的标签不能唯一，所以还需要根据原始关系网络cora_edgelist生成没有关联的点对，作为负样本
#
# 将所有的nodes和除它自身以外的nodes进行组合，形成点对
# 获取出所有的nodes存入列表nodes中
nodes = []
del nodes[:]
gc.collect()
fs = open(sorted_nodes)
for line in fs.readlines():
    nodes.append(line.split('\n')[0])
fs.close()

# 生成所有的点对只是为了从中提取负样本（即没有好友关系的点对）
# 在生成无关联点对的过程中，如果生成了01,就不必在生成10了
gen_nodes_pair = {}
f = open(nodes_pair, 'w')
pairs = []
# 生成无关联点对的计数
count = 0
for node_l in nodes:
    # if count == 13724:
    #     break
    for node_r in nodes:
        # 除自身外
        if node_l != node_r:
            # 检查是否已经生成过了
            if gen_nodes_pair.has_key(str(str(node_l) + ' ' + str(node_r))):
                pass
            else:
                my_str = ''
                my_str_reverse = ''
                my_str += str(node_l) + ' ' + str(node_r)
                my_str_reverse += str(node_r) + ' ' + str(node_l)
                # 需要查一下字典看生成的点对是不是无关的（字典里的key都是有关联的点对，不在字典里的点对就是无关的）
                if dictionary.has_key(my_str):
                    pass
                else:
                    pairs.append(my_str + '\n')
                    gen_nodes_pair[my_str] = '0'
                    gen_nodes_pair[my_str_reverse] = '0'
                    count += 1
        else:
            pass
        # if count == 13724:
        #     break

for pair in pairs:
    f.write(pair)
f.close()

inputs = []
unrelated_len = 0
fn = open(nodes_pair)
for line in fn.readlines():
    unrelated_len += 1
    inputs.append(line.split('\n')[0])
fn.close()


test_unrelated = utils.random_nodes_pair(inputs, float(test_ne_len) / float(len(inputs)))
dictionary_split = {}
f_te_ne = open(test_ne,'w')
for tu in test_unrelated:
    f_te_ne.write(tu + '\n')
    dictionary_split[tu] = '0'
f_te_ne.close()

new_input = []
for ip in inputs:
    if dictionary_split.has_key(ip):
        pass
    else:
        new_input.append(ip)

train_unrelated = utils.random_nodes_pair(new_input, float(train_ne_len) / float(len(new_input)))
f_tr_ne = open(train_ne,'w')
for tu in train_unrelated:
    f_tr_ne.write(tu + '\n')
f_tr_ne.close()
