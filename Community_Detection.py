import community as cl
import pandas as pd
import networkx as nx
import networkx.algorithms.community as nx_comm
import copy 
from datetime import timedelta, date
import json_lines

def get_name():
    return "Omer Rosenberg"
def get_id():
    return 315328898

###part 1 queastion 1
def community_detector(algorithm_name, network, most_valuable_edge = None):
    res = {}
    
    if algorithm_name == "girvan_newman":
        iterator = nx_comm.girvan_newman(network, most_valuable_edge)
        max_modularity = nx_comm.quality.modularity(network, [set(network.nodes())], weight = 'weight')
        res['num_partitions'] = 1
        partition_count = 1
        for partition in iterator:
            modularity = nx_comm.quality.modularity(network, partition, weight = 'weight')
            partition_count += 1
            if modularity > max_modularity:
                max_modularity = modularity
                res['num_partitions'] = partition_count
                res['partition'] = partition
        res['modularity'] = max_modularity
        res['partition'] = [list(res['partition'][i]) for i in range(len(res['partition']))] 

    elif algorithm_name == "louvain":
        best_partition = cl.best_partition(network)
        num_partitions = max(best_partition.values())+1
        lst_best_partition = []
        for i in range(num_partitions):
            lst_best_partition.append([])
        for key in best_partition.keys():
            lst_best_partition[best_partition[key]].append(key)
        res['num_partitions'] = len(lst_best_partition)
        res['modularity'] = nx_comm.quality.modularity(network, lst_best_partition, weight = 'weight')
        res['partition'] = lst_best_partition
        
    else: ###clique_percolation
        memorization = []
        for k in range (2, network.number_of_nodes()):
            partition = list(nx.algorithms.community.k_clique_communities(network,k))
            lst_partition = [list(community) for community in partition]
            lst_partition_copy = copy.deepcopy(lst_partition)
            nodes = []
            for i in range(len(partition)):
                for node in partition[i]:
                    if node in nodes:
                        lst_partition_copy[i].remove(node)
                    else:
                        nodes.append(node)
            for node in network.nodes():
                if node not in nodes:
                    lst_partition_copy.append([node])
            modularity = nx_comm.quality.modularity(network, lst_partition_copy, weight = 'weight')
            memorization.append((k, modularity)) 
        optimal = max(memorization, key = lambda x: x[1])
        optimal_k = optimal[0]
        optimal_partition = list(nx.algorithms.community.k_clique_communities(network, optimal_k))
        res['num_partitions'] = len(optimal_partition)
        res['modularity'] = optimal[1]
        res['partition'] = [list(optimal_partition[i]) for i in range(len(optimal_partition))]
    
    return res

def edge_selector_optimizer(network):
    betweness = nx.edge_betweenness_centrality(network, weight = 'weight')
    return max(betweness, key = betweness.get)

### part 2 question 1 
def construct_heb_edges(files_path, start_date = '2019-03-15', end_date = '2019-04-15', non_parliamentarians_nodes = 0):
    start_d = date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:]))
    end_d = date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:]))
    central_political_players = list(pd.read_csv(files_path + "/central_political_players.csv").id)
    delta = timedelta(days = 1)
    res = {}
    nodes_degrees = {}
    while start_d <= end_d:
        #print(start_d.strftime("%Y-%m-%d"))
        st = start_d.strftime("%Y-%m-%d") + '.txt'
        start_d += delta
        file_name = files_path + '/Hebrew_tweets.json.' + str(st)
        with open(file_name,'rb') as file:
            for retweet in json_lines.reader(file, broken = True):
                if 'retweeted_status' in retweet.keys():
                    key = (retweet['user']['id'], retweet['retweeted_status']['user']['id'])
                    if key in res.keys():
                        res[key] += 1
                    else:
                        res[key] = 1
                        if key[0] in nodes_degrees.keys():
                            nodes_degrees[key[0]] += 1
                        else:
                            nodes_degrees[key[0]] = 1
                        if key[1] in nodes_degrees.keys():
                            nodes_degrees[key[1]] +=1
                        else:
                            nodes_degrees[key[1]] = 1
                            
    for politician in central_political_players:
        try:
            del nodes_degrees[politician]
        except:
            continue
    sorted_nodes_degrees = sorted(nodes_degrees.items(), key = lambda x: x[1], reverse = True)
    if non_parliamentarians_nodes > len(sorted_nodes_degrees):
        return res
    else:
        sorted_nodes_degrees = sorted_nodes_degrees[non_parliamentarians_nodes:]
    keys = copy.deepcopy(tuple(res.keys()))
    for node in sorted_nodes_degrees:
        for key in keys:
            if key[0] == node[0] or key[1] == node[0]:
                try:
                    del res[key]
                except:
                    continue
    return res

def construct_hub_network(edge_dictionary):
    res_net = nx.DiGraph()
    weighted_edges = []
    for key in edge_dictionary.keys():
        weighted_edges.append((key[0],key[1], edge_dictionary[key]))
    res_net.add_weighted_edges_from(weighted_edges)
    return res_net
