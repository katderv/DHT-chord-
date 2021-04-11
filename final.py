import linecache
import os
import sys
from hash_function import hash
import math
import pandas as pd
from time import perf_counter, perf_counter_ns


# Disable printing
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore printing
def enablePrint():
    sys.stdout = sys.__stdout__

def stabilize(sortli, ring_size):
    #stabilizing successors predecessors
    for item in sortli:
        if sortli.index(item) + 1 >= len(sortli):  # if it's the last element
            item.successor = sortli[0]
            item.predecessor = sortli[sortli.index(item) - 1]
        elif item == sortli[0]:  # if it's the first element
            item.successor = sortli[sortli.index(item) + 1]
            item.predecessor = sortli[-1]
        else:
            item.successor = sortli[sortli.index(item) + 1]
            item.predecessor = sortli[sortli.index(item) - 1]

    # stabilizing the finger tables
    for item in sortli:
        fingTemp = []  # create a table for each node
        for i in range(0, int(math.log(ring_size, 2))):
            cand_node = item.id_ + math.pow(2, i)  # candidate node - might not be active
            if cand_node > ring_size:
                cand_node = item.id_ + math.pow(2, i) - ring_size
            for item2 in sortli:  # iterating the list of the sorted nodes to find the element to add to the finger table
                search_node = getattr(item2, 'id_')
                closest_value = cand_node - search_node

                if closest_value <= 0 and cand_node <= sortli[-1].id_:
                    fingTemp.append(item2)
                    break
                elif closest_value > 0 and cand_node <= sortli[-1].id_:
                    continue
                else:
                    fingTemp.append(sortli[0])
                    break

        setattr(item, 'finger', fingTemp)


def leave(list, dlt):  # deletes a node from the ring. It transfer the nodeValues, fixes finger_table etc
    item = lookup(list, list[0], dlt)  # getting the node with id_ == dlt | (item gets the node)
    # Passing the values of the deleting item to its successor before removing it, so they won't be lost
    dlt_nodeValues = item.NodeValues  # nodeValues of deleting item
    suc_nodeValues = getattr(item.successor, 'NodeValues')
    suc_nodeValues.extend(dlt_nodeValues)  # adding the values of the deleting item to its successor
    list.remove(item)  # Removing the item

    stabilize(list, ring_size)

    #printAllValues(list)  # PRINTS


def join(list, add):  # deals when a new node joins the ring. It adds the node, fixes finger_table etc
    print("adding: ", add)
    addnode = Node(add)
    list.append(addnode)  # adding the node to the list

    list = sorted(list, key=lambda item: item.id_)  # sorting the list
    stabilize(list, ring_size)  # stabilizing the list
    # now, the new node has joined the ring with the correct (succ/pred)essor & finger table

    suc = getattr(addnode, 'successor')  # suc = successor node of add (the new node which is joining)
    valueTemp = []  # list with the temporary values which will be add to the new node

    for item in reversed(suc.NodeValues):  # for loop is reversed as not to affect the order of the NodeValues list
        IDvalue = hash(item, ring_size)
        if IDvalue <= addnode.id_ or IDvalue > list[list.__len__() - 1].id_:
            valueTemp.append(item)  # adding the value to the temporary list for the new node
            suc.NodeValues.remove(item)  # REMOVING the value from the successor (old node, not right any more)
    setattr(addnode, 'NodeValues', valueTemp)  # ADDING all the suitable values to the new node

    # PRINTS
    #printAllValues(list)

    return list 


def printAllValues(list):
    for item in list:
        print("For id: ", item.id_)
        for item2 in item.NodeValues:
            IDvalue = hash(item2, ring_size)
            print("id:", item.id_, "idvalue:{}".format(IDvalue), " values: ", item2)



def valueassign(sortli):
    # reading values from csv file and convert to list
    df = pd.read_csv('movies.csv', usecols=["title"]).head(50)
    value_list = df["title"].astype(str).tolist()

    for item in value_list: #iterating list of values
        IDvalue = hash(item, ring_size) #hash value and get id of key
        valueTemp = []
        asnode = lookup(sortli, getattr(sortli[0], 'id_'), IDvalue) #node that value must be held
        #append value to values of node
        if not asnode.NodeValues:
            valueTemp.append(item)
            setattr(asnode, 'NodeValues', valueTemp)
        else:
            valueTemp = asnode.NodeValues
            valueTemp.append(item)
            setattr(asnode, 'NodeValues', valueTemp)


def lookup(sortli, looks, to_find):  # -------------------Search------------------------
    # if int(looks) <= int(to_find):

        for item in sortli:
            finder = item.id_
            if int(str(finder)) == int(str(looks)):
                print("\nWorking with node {}".format(item))
                succs = getattr(item, 'successor')
                pred = getattr(item, 'predecessor')

                if int(str(item)) == int(str(sortli[-1])) and int(to_find) > int(str(item)):
                    return sortli[0]

                elif int(str(item)) == int(str(sortli[-1])) and int(to_find) < int(str(sortli[0])):
                    return sortli[0]

                elif int(str(item)) == int(str(sortli[0])) and int(to_find) > int(str(sortli[-1])):
                    return sortli[0]

                elif int(str(item)) == int(str(sortli[0])) and int(to_find) < int(str(sortli[0])):
                    return sortli[0]



                elif int(str(item)) <= int(to_find):
                    #wanted node is the one we are looking at
                    if int(str(finder)) == int(str(to_find)):  # finder == to_find
                        print("\tKey: {} exists in node with id: {}".format(to_find, item.id_))
                        # print("finder == to_find: {}".format(item.id_))---------------------FIX A PRINT-------------------------
                        return item

                    # wanted node is successor
                    elif int(str(succs)) == int(to_find):
                        print("\tKey: {} exists in node with id: {}".format(to_find, item.successor))
                        return item.successor



                    #to_find among looks and successor
                    elif int(str(succs)) >= int(to_find) and int(finder) < int(to_find):
                        print("\tKey: {} exists in node with id: {}".format(to_find, item.successor))
                        # print("2exist suc: {}".format(i))
                        return item.successor

                    else:

                        print("\tIt's not in {}'s succesor. Iterating finger table...".format(item))
                        for i in range(0,len(item.finger)):
                            node = item.finger[i]
                            #wanted node is the finger we are looking at
                            if int(str(node)) == int(to_find):
                                print("\tKey: {} exists in node with id: {}".format(to_find, node))
                                return node
                            #wanted node among fingers
                            elif i < len(item.finger)-1 and int(str(node)) < int(to_find) and int(str(item.finger[i+1])) > int(to_find):  # and int(str(item)) < int(str(to_find))
                                print("\tKey: {} is among fingers".format(to_find))
                                return lookup(sortli, node, to_find)

                            #wanted node among fingers but finger+1 goes across ring
                            elif i+1 < len(item.finger) and int(str(item.finger[i])) > int(str(item.finger[i+1])) and int(to_find)> int(str(item.finger[i])):
                                print("\tKey: {} is among fingers".format(to_find))
                                return lookup(sortli, node, to_find)
                            #wanted node is greater than fingers
                            elif i+1 == len(item.finger) and int(to_find) > int(str(item.finger[i])):
                                print("\tKey: {} is greater than last finger".format(to_find))
                                return lookup(sortli, item.finger[i], to_find)


                elif int(str(item)) > int(str(to_find)):

                    #case where to_find < first node
                    if int(str(item)) == int(str(sortli[0])):
                        if int(to_find) < int(str(item)):
                            return sortli[0]

                    #wanted node is predecessor
                    elif int(str(pred)) == int(str(to_find)):
                        print("\tKey: {} exists in node with id: {}".format(to_find, item.id_))
                        return item.predecessor

                    #wanted node among pred and looks
                    elif int(str(pred)) < int(to_find) and int(finder) >= int(to_find):
                        print("\tKey: {} exists in node with id: {}".format(to_find, item.id_))
                        return item

                    else:
                        #iterating finger table
                        for j in range(0, len(item.finger)):
                            fing = item.finger[j]
                            #found in finger table
                            if int(str(fing)) == int(str(to_find)):
                                return fing


                            # fing+1 goes around ring and fing+1 < to_find
                            elif j+1 < len(item.finger) and int(str(fing)) >= int(str(item.finger[j+1])) and int(str(item.finger[j+1])) < int(to_find):
                                print("fing+1 goes around ring and fing+1 < to_find")
                                return lookup(sortli, int(str(item.finger[j+1])) , to_find)

                            #fing+1 goes around ring and fing+1 > to_find
                            elif j+1 < len(item.finger) and int(str(fing)) >= int(str(item.finger[j+1])) and int(str(item.finger[j+1])) > int(to_find):
                                print("fing+1 goes around ring and fing+1 > to_find")
                                return lookup(sortli, fing, to_find)

                            #finger doesnt go around ring
                            elif j+1 < len(item.finger) and int(str(item.finger[j])) == int(str(item.finger[-2])) and int(str(fing)) < int(str(item.finger[j+1])):
                                print("finger doesnt go around ring")
                                return lookup(sortli, int(str(item.finger[j + 1])), to_find)




class Node:
    nodes = []

    def __init__(self, id_):
        self.id_ = int(id_)
        Node.nodes.append(self)  # passing each node in a list
        self.successor = 0
        self.predecessor = 0
        self.NodeValues = []

    def __str__(self):
        # return '('+str(self.id_)+')'
        return str(self.id_)


ring_size = int(input("Give the size of the ring: "))  # have a variable to pass the max size of the Chord ring
print("\n\n")


numberofips = int(ring_size * 0.8)

for i in range(numberofips):
    data = linecache.getline('randip.txt', i).strip() #read ips from file
    hashedip = hash(data, ring_size) #get hashed value of ip
    check = True  # Checking if the inserting Node already exists
    for item in Node.nodes:
        if item.id_ == hashedip:
            check = False
    if check == True:  # if it is a new Node, the add it to the ring
        Node(hashedip)

sortli = sorted(Node.nodes, key=lambda item: item.id_) #sort nodes in ascending order to make the ring

blockPrint()
build_and_assign_start = perf_counter()
stabilize(sortli, ring_size)  # calculating the successors, predecessors and finger tables
valueassign(sortli) #assign values on
build_and_assign_stop = perf_counter()
enablePrint()

time_of_build = build_and_assign_stop - build_and_assign_start

for item in sortli:  # printing the ring
    print(item.predecessor, end='\t')
    print(item, end='\t')
    print(item.successor)

print("\n\n")

for item in sortli: #printing finger tables
    print("Node: {}".format(item))
    for n in item.finger:
        print("\t   {}".format(n))

print("\n\nTime of build was: {}".format(time_of_build))

# menu
while True:
    print(
        "\n\nWhat would you like to do next?\n1.Add Node\n2.Delete Node\n3.Show Finger Tables\n4.Print Chord Ring\n5.Search \n6.Print Values of Nodes \n7.Exit")
    sel = input("Choose one: ")
    # """----------------ADD NODE-----------------------------------"""
    if sel == '1':
        tempnum = input("Give the id of the node: ")
        num = hash(tempnum, ring_size)  # HASH NUM - IDnode ###########
        blockPrint()
        join_start = perf_counter()
        while num >= ring_size:
            num = int(input("Give an id smaller than {}: ".format(ring_size)))
        check = True  # Checking if the inserting Node already exists
        for item in sortli:
            if item.id_ == num:
                check = False
        if check == True:  # if it is a new Node, the add it to the ring
            sortli = join(sortli, num)
        join_stop = perf_counter()
        enablePrint()
        # print(check)
        print("node added: {}".format(num))
        time_of_join = join_stop - join_start
        print("Time of join was: {}".format(time_of_join))

    # """----------------CHORD RING-----------------------------------"""
    elif sel == '4':
        # print(sortli)
        for item in sortli:
            print(item.predecessor, end='\t')
            print(item, end='\t')
            print(item.successor)

    # """----------------FINGER TABLES-----------------------------------"""
    elif sel == '3':
        print("\n\n")
        for item in sortli:
            print("Node: {}".format(item))
            for n in item.finger:
                print("\t   {}".format(n))

    # """----------------DELETE-----------------------------------"""
    elif sel == '2':
        dlt = input("Give the id of the node you'd like to delete: ")
        blockPrint()
        leave_start = perf_counter()
        leave(sortli, dlt)
        leave_stop = perf_counter()
        enablePrint()
        time_of_leave = leave_stop - leave_start
        print("Time of leave was: {}".format(time_of_leave))

    # -------------------SEARCH-------------------------------------
    elif sel == '5':
        looks = int(input("Give the node which will execute the lookup: "))
        to_find = input("Give the key you'd like to find: ")
        h_to_find = int(hash(to_find, ring_size))
        # print(h_to_find)
        blockPrint()
        search_start = perf_counter()
        loo = lookup(sortli, looks, h_to_find)  # -----------------passing the return node to loo -------------------
        search_stop = perf_counter()
        enablePrint()
        time_of_search = search_stop - search_start
        print("Time of search was: {}".format(time_of_search))
        for itemm in loo.NodeValues:
            if itemm == to_find:
                print("Movie:{} in node: {}".format(itemm, str(loo.id_)))
    # --------------------AssignValues----------------------------
    elif sel == '6':
        print("Your current ring is:\n")
        for item in sortli:
            print("Values of node {} are:".format(item.id_))
            print(item.NodeValues)
            print("")
    # """----------------EXIT-----------------------------------"""
    elif sel == '7':
        break

    else:
        print("Give valid input")
        continue