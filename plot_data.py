import numpy as np
import os
from matplotlib import pyplot as plt 


def plot_population_chromosome(folder, filename, keyword, save_filename):
    f = open(folder + filename, "r")
    lines = f.readlines()
    seeds = {}
    seed = ''
    individual = 0
    population_averages = {}
    for i in range(len(lines)):
        tokens = lines[i].split(',')
        if tokens[0] == 'seed':
            if seed != '':
                seeds[seed] = np.array(seeds[seed])
                # for i in range(len(seeds[seed][0])):
                #     population_averages[seed]
            seed = tokens[1]
            population_averages[seed] = []
            seeds[seed] = []
            individual = 0
        else:
            seeds[seed].append([])
            for j in range(len(tokens)):
                if tokens[j] == '\n':
                    break
                seeds[seed][individual].append(int(tokens[j]))
            individual += 1
    seeds[seed] = np.array(seeds[seed])
    # take the counts of each population
    counts = []
    seed_keys = list(seeds.keys())
    values = np.unique(seeds[seed])
    for s in range(len(seed_keys)):
        seed_key = seed_keys[s]
        counts.append([])
        for value in values:
            counts[s].append([])
        for col_i in range(seeds[seed_key][0].size):
            col = seeds[seed_key][:,col_i]
            # counting values in column
            for j in range(len(values)):
                count = (col == values[j]).sum()
                counts[s][j].append(count)
    counts = np.array(counts)
    chrom_len = seeds[seed][0].size
    # find the averages
    averages = []

    for j in range(chrom_len):
        data_slice = counts[:,:,j]
        averages.append(np.mean(data_slice, axis=0))
    averages = np.array(averages)

    plt.title(keyword + " Generation Heuristic Occurances") 
    plt.xlabel("Chromosome Position") 
    plt.ylabel("Avg Sum Heuristic Occurances In Population")
    for i in range(len(values)):
        y = averages[:,i]
        x = np.arange(0, chrom_len)
        plt.plot(x, y, label = 'H' + str(values[i])) 
    plt.ylim(0, 100)
    plt.legend()
    plt.rcParams["savefig.directory"] = os.curdir + folder
    save_filename = folder + save_filename + ".png"
    plt.savefig(save_filename)
    #plt.show()
    plt.clf()
    print('saved img:' + save_filename)

def plot_population_edge_options(folder, filename, keyword, save_filename):
    f = open(folder + filename, "r")
    lines = f.readlines()
    seeds = {}
    seed = ''
    individual = 0
    population_averages = {}
    for i in range(len(lines)):
        tokens = lines[i].split(',')
        if tokens[0] == 'seed':
            if seed != '':
                seeds[seed] = np.array(seeds[seed])
                # for i in range(len(seeds[seed][0])):
                #     population_averages[seed]
            seed = tokens[1]
            population_averages[seed] = []
            seeds[seed] = []
            individual = 0
        else:
            seeds[seed].append([])
            for j in range(len(tokens)):
                if tokens[j] == '\n':
                    break
                seeds[seed][individual].append(int(tokens[j]))
            individual += 1
    seeds[seed] = np.array(seeds[seed])
    # take the counts of each population
    counts = []
    chrom_len = seeds[seed][0].size
    seed_keys = list(seeds.keys())
    for i in range(len(seed_keys)):
        counts.append([])
        # for each seed get the average amount of values in each chromosome position
        for j in range(chrom_len):
            col = seeds[seed_keys[i]][:,j]
            avg = np.mean(col)
            counts[i].append(avg)
        # seed_key = seed_keys[s]
        # counts.append([])
        # for value in values:
        #     counts[s].append([])
        # for col_i in range(seeds[seed_key][0].size):
        #     col = seeds[seed_key][:,col_i]
        #     # counting values in column
        #     for j in range(len(values)):
        #         count = (col == values[j]).sum()
        #         counts[s][j].append(count)
    counts = np.array(counts)
    # find the averages
    averages = []

    for j in range(chrom_len):
        data_slice = counts[:,j]
        averages.append(np.mean(data_slice))
    averages = np.array(averages)

    plt.title(keyword + " Generation Ave Population Equidistant Edge Options") 
    plt.xlabel("Chromosome Position") 
    plt.ylabel("Avg Number of Equidistant Edge Options")

    for i in range(len(counts)):
        y = counts[i]
        x = np.arange(0, chrom_len)
        plt.scatter(x, y, color='lightsteelblue') 

    y = averages
    x = np.arange(0, chrom_len)
    plt.plot(x, y, color='red') 

    plt.ylim(0, 10)
    #plt.legend()
    plt.rcParams["savefig.directory"] = os.curdir + folder
    save_filename = folder + save_filename + ".png"
    plt.savefig(save_filename)
    #plt.show()
    plt.clf()
    print('saved img: ' + save_filename)

folder = 'results/gdb8_k2_30_seed/'
plot_population_chromosome(folder, 'last_population_chromosomes.csv', "30 Seed Avg gdb8 k=2\nLast", "last_gen_gdb8_k2_chromosome")
plot_population_chromosome(folder, 'first_population_chromosomes.csv', "30 Seed Avg gdb8 k=2\nFirst", "first_gen_gdb8_k2_chromosome")
plot_population_edge_options(folder, 'last_population_num_edges.csv', "30 Seed Avg gdb8 k=2\nLast", "last_gen_gdb8_k2_edge_options")
plot_population_edge_options(folder, 'first_population_num_edges.csv', "30 Seed Avg gdb8 k=2\nFirst", "first_gen_gdb8_k2_edge_options")
