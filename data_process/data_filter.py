# coding:utf-8
import utils
# 删除轨迹数据中用户轨迹记录不足10条，POI点不足5个的轨迹记录
# 将第一个节点做key，另一个节点value，value是一个list
# adj_dictionary字典里存放了一个用户的所有轨迹，key为用户，value为轨迹
# poi_dictionary字典里存放一个POI在所有轨迹中出现的次数
file_bk_traj = '../data/poi_filter2.txt'

adj_dictionary = {}
poi_dictionary = {}
f_n = open(file_bk_traj)
i = 0
for line in f_n.readlines():
    user = line.replace('\n','').split(' ')[0]
    location = line.replace('\n','').split(' ')[4]
    i += 1
    print i
    # edges_dictionary[user+' '+location] = ''
    if utils.key_in_dic(location, poi_dictionary):
        poi_dictionary[location] += 1
    else:
        poi_dictionary[location] = 0

    if utils.key_in_dic(user,adj_dictionary):
        adj_dictionary[str(user)].append(location)
    else:
        adj_dictionary[str(user)] = list()
        adj_dictionary[str(user)].append(location)
        # adj_dictionary[str(user)] = list(location)不可以这样，如果location是两位数，它会被拆成两个部分
f_n.close()

# 记录不足10条的用户从adj_dictionary中删除，把删除的用户存入user_lst,剩余的轨迹记录存入adj_dictionary1中
condition1 = 0
user_lst = []
adj_dictionary1 = {}
for key,value in adj_dictionary.iteritems():
    if len(adj_dictionary[key]) < 2:
        condition1 += 1
        user_lst.append(key)
    else:
        adj_dictionary1[key] = value

print condition1

# 将删除记录不足10条的用户后，剩余的轨迹记录写入新文件brightkite_location_1.txt中
file_filter1 = '../data/brightkite_filter1.txt'
b_k_t = open(file_bk_traj)
f_f_1 = open(file_filter1,'w')
i = 0
for line in b_k_t.readlines():
    user = line.replace('\n', '').split(' ')[0]
    location = line.replace('\n', '').split(' ')[4]
    i += 1
    print i

    if utils.key_in_dic(user, adj_dictionary1):
        f_f_1.write(line)
    else:
        pass
b_k_t.close()
f_f_1.close()

# #再从poi_dicitonary中删除POI点不足5个的记录,把出现次数不足5次的POI点存入poi_lst中
condition2 = 0
poi_lst = []
poi_dictionary2 = {}
for key,value in poi_dictionary.iteritems():
    if value < 1:
        condition2 += 1
        poi_lst.append(key)
    else:
        poi_dictionary2[key] = value

print 'filter2'

file_filter2 = '../data/brightkite_filter2.txt'
f_f_1 = open(file_filter1)
f_f_2 = open(file_filter2,'w')
i = 0
for line in f_f_1.readlines():
    user = line.replace('\n', '').split(' ')[0]
    location = line.replace('\n', '').split(' ')[4]
    i += 1
    print i

    if utils.key_in_dic(location, poi_dictionary2):
        f_f_2.write(line)
    else:
        pass
f_f_1.close()
f_f_2.close()

#
file_traj = '../data/brightkite_filter2.txt'
# file_traj = '/media/ubuntu-01/ML/BK/poi_filter2.txt'
# user_dicitonary中存放轨迹记录中的用户
user_dicitonary = {}
f_t = open(file_traj)
for line in f_t.readlines():
    user = line.replace('\n', '').split(' ')[0]
    # location = line.replace('\n', '').split(' ')[5]
    user_dicitonary[user] = ''
f_t.close()

file_G = '../data/Gowalla_edges.txt'
file_N = '../data/Brightkite_edges_regular.txt'
# 将‘\t’改为‘ ’
f = open(file_G)
f_n = open(file_N, 'w')
for line in f.readlines():
    new_line = line.replace('\t', ' ')
    f_n.write(new_line)
f_n.close()
f.close()

# 由于社交关系中的用户可能并未出现在轨迹记录中，需要对社交关系中的数据进行清洗
# 这样，social_filter中的用户都能在轨迹记录中找到
file_social = '../data/Brightkite_edges_regular.txt'
file_social_filter = '../data/Brightkite_edges.txt'
f_s = open(file_social)
f_s_f = open(file_social_filter,'w')
for line in f_s.readlines():
    line_l,line_r = utils.get_nodes(line)
    if utils.key_in_dic(line_l,user_dicitonary) and utils.key_in_dic(line_r,user_dicitonary):
        f_s_f.write(line)
    else:
        pass
f_s.close()
f_s_f.close()


# 从处理好的所有边（边的用户一定有对应的轨迹）中获取一个连通的子图
BK_file = '../data/Brightkite_edges.txt'
BK_edges = '../data/edges_undirected.txt' #有01就没有10
nodes_file = '../data/vec_all.txt'#得到向量表示
sorted_nodes = '../data/sorted_nodes.txt'#获得网络中所有点（有序）
nodes_degree = '../data/nodes_degree.txt'#网络中各点的度

# 通过embedding的方式获取全部节点
from gensim.models import word2vec

sentence = word2vec.LineSentence('../data/Brightkite_edges.txt')
model = word2vec.Word2Vec(sentence, size=3, min_count=0, workers=15)
model.wv.save_word2vec_format('../data/vec_all.txt')

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
i = 0
f = open(BK_file)
for line in f.readlines():
    dictionary[line.split('\n')[0]] = '0'
    i += 1
    print '所有关联点对：（428156）', i
f.close()
#
# # 由于BK_file中的点对有重复的（双向：如1 0;0 1）这种应该视为一个有关联的点对，所以需要查找字典
# # 当查找BK_file中的1 0时，将key为1 0和0 1的value都置为1,并将点对写入edges_undirected中
# # 接下来查找0 1,若key的value为1,则跳过它。这样edges_undirected中的点对就只有1 0而没有0 1了
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
print '所有关联点对（214078）'

# 计算社交关系拓扑图中所有节点的度
# 先根据节点文件创建节点字典，字典中所有key的初始值为0
# 遍历整个edges_undirected,每出现一个字符，就更新该字符所对应字典key的value值，将value+1

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
print '各节点的度'

import linecache
# 修改原来关联点对的格式
file_N = '../data/Brightkite_edges.txt'
file_nodes_degree = '../data/nodes_degree.txt'
file_sorted_degree = '../data/sorted_degree.txt'
file_subgraph_pos = '../data/subgraph_positive.txt'
file_subgraph_neg = '../data/subgraph_negative.txt'

# 将节点按照度的大小来排序
dictionary_degree = {}
f_n_d = open(file_nodes_degree)
for line in f_n_d.readlines():
    new_line = line.replace('\n','')
    dictionary_degree[new_line.split(' ')[0]] = int(new_line.split(' ')[1])

f_s_d = open(file_sorted_degree,'w')
sorted_degree_len = 0
for k,v in sorted(dictionary_degree.iteritems(), key=lambda asd:asd[1], reverse=True):
    f_s_d.write(str(k)+' '+str(v)+'\n')
    sorted_degree_len += 1
f_s_d.close()

# 获取度最大的节点，从它关联的点对中在选取度最大的前三个点
# 然后再从这三个点按照相同的方法再发展出3个点
# 一直到200个点就结束

# 将第一个节点做key，另一个节点value，value是一个list
# adj_dictionary字典里存放了社交关系的邻接矩阵
# edges_dictionary字典中存放所有的社交关系
adj_dictionary = {}
edges_dictionary = {}
f_n = open(file_N)
for line in f_n.readlines():
    node_a = line.replace('\n','').split(' ')[0]
    node_b = line.replace('\n','').split(' ')[1]
    edges_dictionary[node_a+' '+node_b] = ''
    if utils.key_in_dic(node_a,adj_dictionary):
        adj_dictionary[str(node_a)].append(node_b)
    else:
        adj_dictionary[str(node_a)] = list()
        adj_dictionary[str(node_a)].append(node_b)
f_n.close()

dictionary_degree = {}
f_n_d = open(file_nodes_degree)
for line in f_n_d.readlines():
    new_line = line.replace('\n','')
    dictionary_degree[new_line.split(' ')[0]] = int(new_line.split(' ')[1])
f_n_d.close()

# # 选择200个节点中的根节点
content = linecache.getline(file_sorted_degree,1)
root_node = content.replace('\n' ,'').split(' ')[0]
save_nodes = []
son_nodes = []
for i in utils.related_three_node(adj_dictionary[root_node],save_nodes,dictionary_degree):
    son_nodes.append(i)
save_nodes.append(root_node)
# 先把选择出的点abc存起来
for node in son_nodes:
    save_nodes.append(node)
# 然后在遍历，以免a选择的三个点中，有bc
for node in son_nodes:
    for i in utils.related_three_node(adj_dictionary[node],save_nodes,dictionary_degree):
        save_nodes.append(i)
        son_nodes.append(i)
    if len(save_nodes) >= 2298:
        break

f_s_p = open(file_subgraph_pos,'w')
f_s_n = open(file_subgraph_neg,'w')

# 将选出的200左右的点找到其关联的边
for node_l in save_nodes:
    for node_r in save_nodes:
        if node_l == node_r:
            pass
        elif utils.key_in_dic(node_l+' ' + node_r, edges_dictionary):
            f_s_p.write(node_l + ' ' + node_r + '\n')
        else:
            f_s_n.write(node_l + ' ' + node_r + '\n')
f_s_p.close()
f_s_n.close()