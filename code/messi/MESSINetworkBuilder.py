#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


from networkx.drawing.nx_pydot import write_dot
from graphviz import Digraph

import pylab
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph

#sudo apt-get install -y graphviz libgraphviz-dev pkg-config python-pip
#sudo pip install pygraphviz

import pygraphviz as pgv
"""
Python module for generating relevant data from a MESSI network.
TODOs:
 1. automatic checking of toricity.
 2. generation of binomials.
 3. graphs of multistationarity.
 4. nicer visualization of network?
"""



class MESSINetwork:
    """
    A class representing a MESSI network, including the derived graphs.

    Parameters
    ----------
        G: DiGraph
            the network digraphs (nodes, edges, and reaction constant names)
        complexes: list of list of ints
            a list of complexes. Each complex a list of species indexes
        species: list of strings
            a list of species names
        partitions: list of list of ints
            a list of the partitions of the messi network. Each partition is a list of species names

        Example:

        complexes = [

        [0, 4], #S0+E

        [1, 4], #S1 + E

        [2], #ES0

        [0, 5], #S0 + F

        [1, 5], #S1 + F

        [3] #FS1

        ]

        species = ['S0', 'S1', 'ES0', 'FS1', 'E', 'F']

        partitions = [['ES0', 'FS1', 'S1P0', 'FP1'],

        ['S0', 'S1'],

        ['P0', 'P1'],

        ['E'],

        ['F']]

    """

    def __init__(self, G=None, complexes=[], species=[], partitions=[], complexes_names=[], species_names=[], partitions_names = [], constants_names = [], test=False):
        """
        Builds a MESSINetwork and the derived graphs.

        """

        self.G = G

        #print("G")
        #print(G.edges(data=True))

        self.complexes = complexes

        self.species = species

        self.complexes_names = complexes_names
        self.species_names = species_names

        self.constants_names = constants_names

        #Nasty hack
        if not test:
            self.partitions = partitions
            self.partitions_names = partitions_names
            self.G1 = self.buildG1()
            self.G2 = self.buildG2()
            self.G2_circle = self.buildG2_circle()
        else:
            self.G2 = None
            self.G2_circle = None
            self.partitions = None
            self.partitions_names = None

        self.linear_relations = self.buildLinearRelations()



    def reacts_via_intermediates_starting_from_partitions(self, alpha, intermediate):

       #print("complexes", self.complexes)
       #print("complexes_names", self.complexes_names)
       intermediates = self.partitions[0]
       intermediate_index = self.complexes.index([intermediate])

       P = self.partitions[alpha]
       for complex_index, complex in enumerate(self.complexes):
           found_complex = False
           for species in complex:
               if species in P:

                   #Deberia parar si ya entre una vez...
                   found_complex = True
                   #print("G", self.G.edges())
                   #print(complex)
                   #print(intermediate)
                   simple_paths = nx.all_simple_paths(self.G, complex_index, intermediate_index)

                   L = list(simple_paths)

                   for simple_path in L:

                       only_goes_through_intermediates=True
                       #print("simple path")
                       #print(simple_path)

                       #Ignoramos las puntas
                       for index, c in enumerate(simple_path[1:-1]):
                           #print(self.complexes[c])
                           for species_index in self.complexes[c]:
                               #print("species")
                               #print(self.species[species_index])

                               #TODO los intermediates deberian ser indices o nombres?
                               #Me parece que es mas facil que sean indices
                               if species_index not in intermediates:
                                   #we could also break the loops here.
                                   only_goes_through_intermediates=False

                       if only_goes_through_intermediates:
                           return True
       return False



    def buildLinearRelations(self):
        '''builds linear relations as described in Notation 11 in the arxiv paper'''

        relations = []
        for alpha in range(1, len(self.partitions)):
            ks = []
            for intermediate in self.partitions[0]:
                if self.reacts_via_intermediates_starting_from_partitions(alpha, intermediate):
                    ks.append(intermediate)


            for species in self.partitions[alpha]:
                ks.append(species)

            relations.append(ks)

        return relations

    def intermediates(self):
        """Retrieves a list of the intermediate complexes

        Retrieves a list of the intermediate complexes,
        i.e., the elements of the first partition of the MESSINetwork.

        Args: None

        Returns: a list of the intermediate complexes

        """

        return self.partitions_names[0]

    def get_species_vector_from_complex_name(self, complex_name):
        ret = []
        for species_index in complex_name:
            ret.append(self.species_names[species_index])
        return ret

    def core_complexes(self):
        core_complexes = []
        for complex_index, complex in enumerate(self.complexes):
            found = False
            species_vector = self.get_species_vector_from_complex_name(complex)
            for species in species_vector:
                if species in self.partitions_names[0]:
                    found = True
            if not found:
                core_complexes.append(complex_index)

        return core_complexes

        """return [complex_index for complex_index in self.complexes\
         if self.get_species_vector_from_complex_name(self.complexes[complex_index]) \
          not in self.partitions_names[0]]"""

        """L = []
        for partition in self.partitions_names[1:]:
            L += partition
        #print("L")
        #print(L)

        L_indices = []
        for index, complex_name in enumerate(self.complexes_names):
            #print(complex_name)
            found=True
            for i in complex_name:
                #print("self.species[i]: ")
                #print(self.species[i])
                print(self.species_names)
                print(i)
                print("L")
                print(L)
                if self.species_names[i] not in L:
                    found=False
            if found:
                L_indices.append(index)
                print("Core")
                print(complex_name)
        print("L indices")
        print(L_indices)
        return L_indices"""

    def complexes_reactions_by_intermediates(self, core_complexes, intermediates):
        new_edges = []

        #print("core complexes")
        #print(core_complexes)

        #print("intermediates")
        #print(intermediates)

        for source in core_complexes:
            for target in core_complexes:
                #Deberia bastar solo los simple paths. Chequear
                simple_paths = nx.all_simple_paths(self.G, source, target)

                L = list(simple_paths)

                for simple_path in L:

                    only_goes_through_intermediates=True
                    #print("simple path")
                    #print(simple_path)

                    #Ignoramos las puntas
                    for index, c in enumerate(simple_path[1:-1]):
                        #print(self.complexes[c])
                        for species_index in self.complexes[c]:
                            #print("species")
                            #print(self.species[species_index])

                            #TODO los intermediates deberian ser indices o nombres?
                            #Me parece que es mas facil que sean indices
                            if self.species_names[species_index] not in intermediates:
                                #we could also break the loops here.
                                only_goes_through_intermediates=False

                    if only_goes_through_intermediates:
                        new_edges.append([source, target])

        #print("new edges: ")

        return new_edges

    def buildG1(self):
        vertices = self.core_complexes()

        edges = self.complexes_reactions_by_intermediates(vertices, self.partitions_names[0])


        G1_nx = nx.DiGraph(directed=True)

        sources = set([reaction[0] for reaction in edges])

        targets = set([reaction[1] for reaction in edges])

        nodes = sources.union(targets)
        G1_nx.add_nodes_from(nodes)
        for index, reaction in enumerate(edges):
            label = ("t%d" % index)
            G1_nx.add_edge(reaction[0], reaction[1], reaction_constant=label)

        return G1_nx

    def monomolecular(self, complex1, complex2):
        return len(complex1) == 1 and len(complex2) == 1


    def get_partition(self, species):
        for partition in self.partitions:
            if species in partition:
                return partition

    def get_pairs_from_same_partition(self, complex1, complex2):

        #print("complexes: ")
        #print(complex1)
        #print(complex2)
        if self.get_partition(complex1[0]) == self.get_partition(complex2[0]):
            assert(self.get_partition(complex1[1]) == self.get_partition(complex2[1]))
            first_pair = [complex1[0], complex2[0]]
            first_label = complex1[1]

            second_pair = [complex1[1], complex2[1]]
            second_label = complex1[0]

        else:
            assert(self.get_partition(complex1[0]) == self.get_partition(complex2[1]))
            assert(self.get_partition(complex1[1]) == self.get_partition(complex2[0]))


            #Labels are the other origins
            first_pair = [complex1[0], complex2[1]]
            first_label = complex1[1]

            second_pair = [complex1[1], complex2[0]]
            second_label = complex1[0]


        L = [[first_pair, first_label], [second_pair, second_label]]
        #print("for G2:")
        #print(L)

        return L
        """complexes = complex1 + complex2
        pairs = []
        for partition in partitions:
            L = []
            for complex in complexes:
                if complex in partition:
                    L.append(complex)
                    complexes.remove(complex)
                if len(L) == 2:

                    #the label is the other 2 complexes - that's all we need
                    label = L + complexes
                    pairs.append([L,label])

        assert(len(pairs) == 2)
        return pairs"""


    def buildG2(self):
        if self.G1 == None:
            self.buildG1();

        #nodes = self.core_complexes()

        #nodes = set()
        G2_nx = None
        G2_nx = nx.DiGraph(directed=True)
        #G2_nx.add_nodes_from(nodes)

        for edge in self.G1.edges(data=True):
            complex1 = self.complexes[edge[0]]
            complex2 = self.complexes[edge[1]]

            if self.monomolecular(complex1, complex2):
                #I add it as is

                #Guardamos las especies directamente en G2
                G2_nx.add_edge(self.complexes[edge[0]][0],
                               self.complexes[edge[1]][0], reaction_constant=edge[2]['reaction_constant'])

                #nodes.add(edge[0])

                #nodes.add(edge[1])
            else:
                #If X1 + X2 -> X3 + X4, with X1 and X3 in the same partition,
                #and the same for X2 and X4,
                #we build edges X1-> X4

                PAIR=0
                LABEL=1
                first, second = \
                    self.get_pairs_from_same_partition(complex1, complex2)

                #nodes.add(first[PAIR][0])
                #nodes.add(first[PAIR][1])
                #nodes.add(second[PAIR][0])
                #nodes.add(second[PAIR][1])

                #Faltan los labels...
                #print("first, second")
                #print(first)
                #print(second)

                species1 = first[PAIR][0]
                species2 = first[PAIR][1]
                species3 = second[PAIR][0]
                species4 = second[PAIR][1]

                """new_complexes = []

                for species in [species1, species2, species3, species4]:
                    if [species] not in self.complexes:
                        self.complexes.append([species])
                        self.complexes_names.append([self.species_names[species]])
                    new_complexes.append(self.complexes.index([species]))"""


                G2_nx.add_edge(species1, species2, reaction_constant=first[LABEL])

                G2_nx.add_edge(species3, species4, reaction_constant=second[LABEL])


        nodes = []
        for edge in G2_nx.edges():
            if edge[0] not in nodes:
                nodes.append(edge[0])

            if edge[1] not in nodes:
                nodes.append(edge[1])

        G2_nx.add_nodes_from(nodes)

        #G2_nx.add_nodes_from(nodes_vector)
        #print(G2_nx.nodes())
        return G2_nx


    #Chequear que los labels de los monomoleculares sean los correctos
    def buildG2_circle(self):
        G2_circle = self.G2.copy()
        G2_circle.remove_edges_from(nx.selfloop_edges(G2_circle))

        nodes_to_remove = []
        for node in G2_circle.nodes():
            found = False
            for edge in G2_circle.edges():
                if node in edge:
                    found = True
            if not found:
                nodes_to_remove.append(node)


        G2_circle.remove_nodes_from(nodes_to_remove)
        return G2_circle


def plot_as_multi_digraph(G):
    reaction_constants = nx.get_edge_attributes(G,'reaction_constant')
    #print(reaction_constants)
    """Gm = nx.MultiDiGraph()
    for edge in G.edges():
        Gm.add_edge(edge[0], edge[1], reaction_constant=reaction_constants[edge])"""

    """df = pd.DataFrame(index=Gm.nodes(), columns=Gm.nodes())
    for row, data in nx.shortest_path_length(Gm):
        for col, dist in data.items():
            df.loc[row,col] = dist

    df = df.fillna(df.max().max())

    layout = nx.kamada_kawai_layout(Gm, dist=df.to_dict())
    nx.draw(G,layout,arrows=True, edge_color='black',width=1,linewidths=1,\
node_size=500,node_color='pink',alpha=0.9,arrowsize=12,arrowstyle='-|>',\
labels={node:node for node in G.nodes()},
)

    edge_labels = nx.get_edge_attributes(Gm,'reaction_constant')


    nx.draw_networkx_edge_labels(Gm, pos=layout, edge_labels = edge_labels)

    if not debug:
        plt.show()"""
    #write_dot(G,'multi2')
    G.graph['graph']={'rankdir':'TD'}
    G.graph['node']={'shape':'circle'}
    G.graph['edges']={'arrowsize':'4.0'}




    """for edge in G.edges():
        #print(edge[0])
        #print(edge[1])
        A.add_edge(edge[0], edge[1])
        #print(A)
        #exit(0)
        #horrible hack. https://stackoverflow.com/questions/15455855/how-to-add-and-show-weights-on-edges-of-a-undirected-graph-using-pygraphviz
        print(A)
        a_edge = A.get_edge(edge[0], edge[1])
        a_edge.attr['label'] = reaction_constants[edge]"""

    #See https://stackoverflow.com/questions/39657395/how-to-draw-properly-networkx-graphs
    #we are creating it manually...
    A = to_agraph(G)



    #print(A)
    #print(reaction_constants)
    for edge in G.edges():
        #print(edge)
        a_edge = A.get_edge(edge[0], edge[1])
        a_edge.attr['label'] = reaction_constants[edge]

    #print(A)


    #See https://pygraphviz.github.io/documentation/pygraphviz-1.3rc1/reference/agraph.html
    #WHERE ARE THE OTHER ATTRIBUTES?
    #Maybe check https://pygraphviz.github.io/documentation/pygraphviz-1.5/tutorial.html#attributes

    #Update: this is the complete documentation - I think. https://graphviz.gitlab.io/_pages/doc/info/attrs.html
    #See also https://www.contentful.com/blog/2018/05/04/using-graphviz-to-visualize-structured-content-from-contentful-spaces/
    """A.node_attr.update(color='red')
    A.edge_attr.update(len='2.0',color='blue')
    A.graph_attr.update(label= '(Expanded) Phosphorylation cascade',
        decorate=True, dim=3
        )"""

    A.node_attr.update(
        shape='circle', width=0.3, fixedsize='shape', margin=0, style='filled', fontname='Helvetica', color='#23a6db66', fontsize=8
        )

    A.edge_attr.update(
    fontname='Helvetica', color='blue', fontcolor='blue', fontsize=8
    )

    A.graph_attr.update(
        pack=True, rankdir='TD', bgcolor='transparent', fontname='Helvetica', fontcolor='blue', fontsize=8,
        label= '(Expanded) Phosphorylation cascade', decorate=True
        )


    #circo and dot are nice
    #neato, twopi
    for var in ['circo', 'dot']:
        #print(var)
        A.layout(prog=var)
        A.draw('phosphorylation_cascade_%s.png' % var)
    #dot = Digraph()
    #dot.render('multi', view=True)

def get_network(debug = False):
    reactions = []
    species_names = []
    species = []
    complexes_names = []
    complexes = []
    if not debug:

        print ("Welcome to an implementation of Algorithm 1 of the paper The structure of MESSI biological systems.")

        print ("Please, input the graph G corresponding to the reaction network you want to analyze.")
        from_file = input("Do you prefer to input the graph from a txt file instead of using the command line? (YES/NO. Default: YES)\n")


        if 'y' in from_file.lower() or len(from_file) == 0:
            filename = input ("Please input the name of the file. Default name: data/network.txt\n")
            if len(filename) == 0:
                filename = 'data/network.txt'
            with  open(filename, "r") as file:
                lines = [line.rstrip('\n') for line in file]
                for line in lines:
                    if ',' not in line:
                        continue
                    r = line[1:-1].split(',')
                    r = [x.strip() for x in r]
                    reactions.append(r)
        else:
            print ('Please input the graph via the command line.')
            print ("Input each reaction with the following format: (SOURCE COMPLEX, TARGET COMPLEX, REACTION_CONSTANT)")
            print ("One example would be: (S0 + E, ES0, k1).")
            print ("When finished, enter the command END")

        #Descomentar para Alicia

            r_input = input()
            while r_input != 'END':
                if ',' in r_input:
                    r = r_input[1:-1].split(',')
                    r = [x.strip() for x in r]
                    reactions.append(r)
                    r_input = input()
    else:
        reactions = [
        ['S0+E', 'ES0','k1'],
        ['ES0', 'S0+E', 'k2'],
        ['ES0', 'S1+E','k3'],

        ['S1+F', 'FS1', 'k4'],
        ['FS1', 'S1+F', 'k5'],
        ['FS1', 'S0+F', 'k6'],

        ['P0+S1','S1P0', 'k7'],
        ['S1P0', 'P0+S1', 'k8'],
        ['S1P0','P1+S1', 'k9'],

        ['P1+F','FP1', 'k10'],
        ['FP1','P1+F', 'k11'],
        ['FP1','P0+F', 'k12']]
        """reactions = [
        ['S01+E','Y01','k11'],
        ['Y01','S01+E','k12'],
        ['Y01','S11+E','k13'],
        ['S11+F','Y11','t11'],
        ['Y11','S11+F','t12'],
        ['Y11','S01+F,t13'],
        ['S02+S11','Y02','k21'],
        ['Y02','S02+S11','k22'],
        ['Y02','S12+S11','k23'],
        ['S12+F','Y12','t21'],
        ['Y12','S12+F','t22'],
        ['Y12','S02+F','t23'],
        ['S03+S12','Y03','k31'],
        ['Y03','S03+S12','k32'],
        ['Y03','S13+S12','k33'],
        ['S13+F','Y13','t31'],
        ['Y13','S13+F','t32'],
        ['Y13','S03+F','t33']]"""


    species_index = 0
    reactions_only_indices = []
    constants_names = []
    for reaction in reactions:
        reaction_only_indices = []
        constants_names.append(reaction[2])
        #[:2] So we don't get the coefficients
        for complex_name in reaction[:2]:
            complex_numbers = []
            for s in complex_name.split('+'):
                s = s.strip()
                if s not in species_names:
                    species_names.append(s)
                    species.append(species_index)
                    complex_numbers.append(species_index)
                    species_index += 1
                else:
                    complex_numbers.append(species_names.index(s))
            #the complex might not be new
            if complex_name not in complexes_names:
                complexes_names.append(complex_name)
                complexes.append(complex_numbers)

            #The reaction as [complex_origin_index, complex_target_index]
            reaction_only_indices.append(complexes.index(complex_numbers))
        #Coefficient
        reaction_only_indices.append(reaction[2])

        reactions_only_indices.append(reaction_only_indices)

    #This part needs some work.
    #I think we should use a multigraph for (label) visualization but a digraph for computations
    G_to_show = nx.DiGraph(directed=True)

    sources = set([reaction[0] for reaction in reactions])
    targets = set([reaction[1] for reaction in reactions])
    nodes = sources.union(targets)


    G_to_show.add_nodes_from(nodes)
    for reaction in reactions:
        G_to_show.add_edge(reaction[0], reaction[1], reaction_constant=reaction[2])

    df = pd.DataFrame(index=G_to_show.nodes(), columns=G_to_show.nodes())
    for row, data in nx.shortest_path_length(G_to_show):
        for col, dist in data.items():
            df.loc[row,col] = dist

    df = df.fillna(df.max().max())

    layout = nx.kamada_kawai_layout(G_to_show, dist=df.to_dict())

    #pos = nx.spring_layout(G)

    plot_as_multi_digraph(G_to_show)

    G = nx.DiGraph(directed=True)

    sources_names = set([reaction[0] for reaction in reactions])
    targets_names = set([reaction[1] for reaction in reactions])
    nodes = sources.union(targets)

    #print(reactions_only_indices)
    G.add_nodes_from(nodes)
    for reaction in reactions_only_indices:
        G.add_edge(reaction[0], reaction[1], reaction_constant=reaction[2])

    #exit(0)

    #nx.draw(G,layout,arrows=True, edge_color='black',width=1,linewidths=1,\
    #node_size=500,node_color='pink',alpha=0.9,arrowsize=12,arrowstyle='-|>',\
    #labels={node:node for node in G.nodes()},
    #)


    #edge_labels = nx.get_edge_attributes(G,'reaction_constant')
    #nx.draw_networkx_edge_labels(G, pos=layout, edge_labels = edge_labels)

    if True:
        plt.show()

    if True:
        answer = ""
    answer = input("Does the network have a MESSI structure? (YES/NO. Default: YES)\n").lower()

    if 'y' in answer.lower() or len(answer) == 0:

        P0_intermediates = []
        P_cores = []

        if True:
            print('.'*30)
            print("Great! Then if it's s-toric we will be able to check multistationarity.")
            print('.'*30)
            print('')
            print('Please write down the partitions of this messi network.')

            from_file = input("Do you prefer to input them from a file instead of using the command line? (YES/NO. Default: YES)\n")

            if 'y' in from_file.lower() or len(from_file) == 0:
                filename = input ("Please input the name of the file. Default name: data/partitions.txt\n")
                if filename == '':
                    filename = 'data/partitions.txt'
                with  open(filename, "r") as file:
                    lines = [line.rstrip('\n') for line in file]
                    core_nodes = False
                    i = 1
                    P = []
                    for line in lines:
                        node = line.strip()

                        if node == 'END' and not core_nodes:
                            core_nodes = True
                            continue

                        if not core_nodes:
                            P0_intermediates.append(node)
                        else:
                            if 'END' in node:
                                i = i+1
                                new_P = P.copy()
                                P_cores.append(new_P)
                                P = []
                            else:
                                P.append(node)
                #print(P0_intermediates)
                #print(P_cores)
            else:
                print("Please introduce the species for S^(0) using the command line. Write END and press ENTER when finished:")
                node = ""
                while(node != "END"):
                    node = input()
                    if node != "END":
                        P0_intermediates.append(node)

                i = 1
                #TODO: falta chequear que no sean vacios y hay al menos 1.
                node = ""
                while(node != "END_CORES"):
                    print("Please introduce the species for S^(%d). Press END to advance to the next set of species and END_CORES to let us know this was the last set." % i)

                    node = ""
                    i = i+1
                    P = []
                    while(node != "END" and node != "END_CORES"):
                        node = input()
                        if node != "END" and node != "END_CORES":
                            P.append(node)

                    P_cores.append(P)
        else:
            P0_intermediates=['ES0','FS1','S1P0','FP1']
            P_cores=[['S0','S1'],['P0','P1'],['E'],['F']]

            """P0_intermediates=  ['Y01','Y11','Y02','Y12','Y03','Y13']
            P_cores = [['E', 'F'], []]"""

        #TODO: check it.
        print("We are trusting you that this is an s-toric MESSI structure!")

        cores = [y for x in P_cores for y in x]

        is_s_toric = True

        #Comentado hasta que lo arregle
        """print("Checking condition C'...")
        for intermediate in P0_intermediates:
            #print("checking intermediate complex %s..." % intermediate)

            simple_o_paths_from_core_source = 0
            for source in sources:

                #Deberia bastar solo los simple paths. Chequear
                simple_paths = nx.all_simple_paths(G, source, intermediate)

                L = list(simple_paths)

                for simple_path in L:
                    only_goes_through_intermediates=True
                    source = simple_path[0]

                    if source not in P0_intermediates:
                        for index, c in enumerate(simple_path):
                            if index > 0:
                                if c not in P0_intermediates:
                                    only_goes_through_intermediates=False
                                    break;
                        if only_goes_through_intermediates:
                            #print("Path %s only goes through intermediates" % simple_path)

                            simple_o_paths_from_core_source = simple_o_paths_from_core_source +1


            #TODO: tal vez esto se puede mejorar
            if simple_o_paths_from_core_source!=1:
                is_s_toric=False
                break

        if is_s_toric:
            print("Condition C' holds!")
        else:
            #TODO no me está dando!!
            print("Condition C' doesn't hold, so the network is not necessarily toric")"""

        print("")
        #print("")
        #print("TODO: check other conditions.")
        #print("Assuming the network is s-toric, by Theorem 4.8, it's toric.")
        #print("Morover, if there is a unique simple path between each node of the graph G2, the exponents of the binomials can be explicitely computed:")
        #print("to be continued...")
        #print("")

        if not debug:
            var = input("Press ENTER to continue with the program.")

        #TODO: finish.

        partitions_names = []
        partitions_names.append(P0_intermediates)
        for core_partition in P_cores:
            partitions_names.append(core_partition)
        partitions = []
        for partition_name in partitions_names:
            partition_indices = []
            for species_name in partition_name:
                partition_indices.append(species_names.index(species_name))
            partitions.append(partition_indices)

    return MESSINetwork(G, complexes, species, partitions, complexes_names, species_names, partitions_names, constants_names)

'''
Para el primer mensaje:

(S0+E, ES0, k1)
(ES0, S0+E, k2)
(ES0, S1+E,k3)
(S1+F, FS1, k4)
(FS1, S1+F, k5)
(FS1, S0+F, k6)
(P0+S1,S1P0, k7)
(S1P0, P0+S1, k8)
(S1P0,P1+S1, k9)
(P1+F,FP1, k10)
(FP1,P1+F, k11)
(FP1,P0+F, k12)
END

'''

#P0_intermediates=[ES0,FS1,S1P0,FP1]
#P_cores=[[S0,S1],[P0,P1],[E],[F]]
'''

Para el segundo mensaje:

ES0
FS1
S1P0
FP1
END
S0
S1
END
P0
P1
END
E
END
F
END_CORES
'''




def get_network_from_text(network_rows, partitions):
    reactions = []
    species_names = []
    species = []
    complexes_names = []
    complexes = []
    lines = network_rows
    for line in lines:
        if ',' not in line:
            continue
        r = line[1:-1].split(',')
        r = [x.strip() for x in r]
        reactions.append(r)

    species_index = 0
    reactions_only_indices = []
    constants_names = []
    for reaction in reactions:
        reaction_only_indices = []
        constants_names.append(reaction[2])
        #[:2] So we don't get the coefficients
        for complex_name in reaction[:2]:
            complex_numbers = []
            for s in complex_name.split('+'):
                s = s.strip()
                if s not in species_names:
                    species_names.append(s)
                    species.append(species_index)
                    complex_numbers.append(species_index)
                    species_index += 1
                else:
                    complex_numbers.append(species_names.index(s))
            #the complex might not be new
            if complex_name not in complexes_names:
                complexes_names.append(complex_name)
                complexes.append(complex_numbers)

            #The reaction as [complex_origin_index, complex_target_index]
            reaction_only_indices.append(complexes.index(complex_numbers))
        #Coefficient
        reaction_only_indices.append(reaction[2])

        reactions_only_indices.append(reaction_only_indices)

    #This part needs some work.
    #I think we should use a multigraph for (label) visualization but a digraph for computations
    G_to_show = nx.DiGraph(directed=True)

    sources = set([reaction[0] for reaction in reactions])
    targets = set([reaction[1] for reaction in reactions])
    nodes = sources.union(targets)


    G_to_show.add_nodes_from(nodes)
    for reaction in reactions:
        G_to_show.add_edge(reaction[0], reaction[1], reaction_constant=reaction[2])

    df = pd.DataFrame(index=G_to_show.nodes(), columns=G_to_show.nodes())
    for row, data in nx.shortest_path_length(G_to_show):
        for col, dist in data.items():
            df.loc[row,col] = dist

    df = df.fillna(df.max().max())

    layout = nx.kamada_kawai_layout(G_to_show, dist=df.to_dict())

    #pos = nx.spring_layout(G)

    plot_as_multi_digraph(G_to_show)

    G = nx.DiGraph(directed=True)

    sources_names = set([reaction[0] for reaction in reactions])
    targets_names = set([reaction[1] for reaction in reactions])
    nodes = sources.union(targets)

    #print(reactions_only_indices)
    G.add_nodes_from(nodes)
    for reaction in reactions_only_indices:
        G.add_edge(reaction[0], reaction[1], reaction_constant=reaction[2])

    #exit(0)

    #nx.draw(G,layout,arrows=True, edge_color='black',width=1,linewidths=1,\
    #node_size=500,node_color='pink',alpha=0.9,arrowsize=12,arrowstyle='-|>',\
    #labels={node:node for node in G.nodes()},
    #)


    #edge_labels = nx.get_edge_attributes(G,'reaction_constant')
    #nx.draw_networkx_edge_labels(G, pos=layout, edge_labels = edge_labels)


    P0_intermediates = []
    P_cores = []

    lines = partitions
    core_nodes = False
    i = 1
    P = []
    for line in lines:
        node = line.strip()

        if node == 'END' and not core_nodes:
            core_nodes = True
            continue

        if not core_nodes:
            P0_intermediates.append(node)
        else:
            if 'END' in node:
                i = i+1
                new_P = P.copy()
                P_cores.append(new_P)
                P = []
            else:
                P.append(node)

    partitions_names = []
    partitions_names.append(P0_intermediates)
    for core_partition in P_cores:
        partitions_names.append(core_partition)
    partitions = []
    for partition_name in partitions_names:
        partition_indices = []
        for species_name in partition_name:
            partition_indices.append(species_names.index(species_name))
        partitions.append(partition_indices)

    return MESSINetwork(G, complexes, species, partitions, complexes_names, species_names, partitions_names, constants_names)
