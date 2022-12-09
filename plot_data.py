import numpy as np
from matplotlib import pyplot as plt 


def plot_population_chromosome(filename, keyword):
    f = open("results/" + filename, "r")
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
    plt.legend()
    plt.show()
    print()


plot_population_chromosome('howe1_k2_30_seed/last_population_chromosomes.csv', "30 Seed Avg Howe1 k=2 Last")
