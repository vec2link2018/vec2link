# coding:utf-8
import utils

# 将第一个节点做key，另一个节点value，value是一个list
# adj_dictionary字典里存放了一个用户的所有轨迹，key为用户，value为轨迹
file_bk_traj = '../data/brightkite_filter2.txt'

adj_dictionary = {}
# edges_dictionary = {}
f_n = open(file_bk_traj)
i = 0
for line in f_n.readlines():
    user = line.replace('\n','').split(' ')[0]
    location = line.replace('\n','').split(' ')[4]
    i += 1
    print i
    # edges_dictionary[user+' '+location] = ''
    if utils.key_in_dic(user,adj_dictionary):
        adj_dictionary[str(user)].append(location)
    else:
        adj_dictionary[str(user)] = list()
        adj_dictionary[str(user)].append(location)

f_n.close()

# # 获取在社交关系中节点的轨迹(列出用户去过的所有locationid，如用户0去过1 2 2 3 3 4，则他的user_traj为1 2 2 3 3 4)
user_file = '../data/sorted_nodes1.txt'
doc_file = '../data/user_traj.txt'
f_b_u = open(doc_file,'w')
f_u = open(user_file)
for line in f_u.readlines():
    if utils.key_in_dic(line.split('\n')[0],adj_dictionary):
        j = 0
        for sub_trah in adj_dictionary[line.split('\n')[0]]:
            j += 1
            if j == len(adj_dictionary[line.split('\n')[0]]):
                f_b_u.write(sub_trah + '\n')
            else:
                f_b_u.write(sub_trah + ' ')
    # 社交关系中的用户无轨迹数据
    else:
        print 'lost user', line
        f_b_u.write('\n')
f_b_u.close()
f_u.close()

# 获取选择出的用户记录
poi_file = '../data/user_poi.txt'
p_f = open(poi_file,'w')
f_b_t = open(file_bk_traj)
u_f = open(user_file)
user_dict = {}
for line in u_f.readlines():
    user_dict[line.split()[0]] = ''
u_f.close()

for line in f_b_t.readlines():
    if utils.key_in_dic(line.replace('\n','').split('\t')[0],user_dict):
        p_f.write(line)
    else:
        pass
f_b_t.close()
p_f.close()



# 使用Doc2vec将用户的轨迹数据转换为向量
from gensim.models.doc2vec import TaggedLineDocument, Doc2Vec
user_tranj_vec = '../data/user_tranj_vec.txt'

documents = TaggedLineDocument(doc_file)
model = Doc2Vec(documents, size=128, negative=10, window=8, hs=0, min_count=0, workers=15, iter=30)

user_id_list = []
u_f = open(user_file)
for line in u_f:
    user_id_list.append(line.split('\n')[0])
u_f.close()

# 不给doc2vec的向量添加用户id信息,每行的轨迹向量对应sorted_nodes中的用户ID
assert len(user_id_list) == len(model.docvecs)
# model.save(save_path)
f_s = open(user_tranj_vec, 'w')
for i, docvec in enumerate(model.docvecs):
    j = 0
    for v in docvec:
        j += 1
        if j == len(docvec):
            f_s.write(str(v) + '\n')
        else:
            f_s.write(str(v) + ' ')
f_s.close()


# 通过embedding的方式获取全部POI
# 这些POI是挑选出的关联点对用户的轨迹点的集合
from gensim.models import word2vec

sentence = word2vec.LineSentence('../data/user_traj.txt')
model = word2vec.Word2Vec(sentence, size=5, min_count=0, workers=15)
model.wv.save_word2vec_format('../data/tmp_traj_vec.txt')

# 统计这些POI出现的次数，进行筛选
user_traj = '../data/user_traj.txt'
poi_all = '../data/tmp_traj_vec.txt'
poi_frequency = '../data/poi_frequency.txt'

poi_dictionary = {}

p_a = open(poi_all)
next(p_a)
for line in p_a:
    poi_dictionary[line.split()[0]] = 0
p_a.close()

u_t = open(user_traj)
for line in u_t.readlines():
    for element in line.split():
        if utils.key_in_dic(element,poi_dictionary):
            poi_dictionary[element] += 1
        else:
            print element
u_t.close()

# poi点及其出现的次数
p_f = open(poi_frequency,'w')
for key,value in poi_dictionary.iteritems():
    p_f.write(key+' '+str(value)+'\n')
p_f.close()

# 删除掉出现次数较少的poi点后的poi点及其出现的次数的记录
poi_filter = {}
poi_freq_update = '../data/poi_frequency_update.txt'
p_f_u = open(poi_freq_update,'w')
for key,value in poi_dictionary.iteritems():
    if value < 3:
        pass
    else:
        poi_filter[key] = ''
        p_f_u.write(key+' '+str(value)+'\n')
p_f_u.close()

# 删除用户轨迹中的一些出现次数较少的poi点
user_traj_update = '../data/user_traj_update.txt'
u_t = open(user_traj)
u_t_u = open(user_traj_update,'w')
for line in u_t.readlines():
    count = 0
    for element in line.split()[:]:
        count += 1
        if utils.key_in_dic(element,poi_filter):
            if count == len(line.split()[:]):
                u_t_u.write(element+'\n')
            else:
                u_t_u.write(element+' ')
        else:
            pass
u_t_u.close()
u_t.close()
