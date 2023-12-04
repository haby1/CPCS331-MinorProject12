import networkx as nx

from matplotlib import pyplot as plt
import pandas as pd

def visualize_graph(G):
    pos = nx.spring_layout(G, k=2.5)
    nx.draw(G, pos, with_labels=True, node_size=900, node_color="skyblue", font_size=8, width=3, edge_color="g",
            font_weight='normal', arrows=True)  # Set arrows=True for directed graph

    edge_labels = nx.get_edge_attributes(G, 'relationship')

    label_pos_adjusted = {}
    for (node1, node2), label in edge_labels.items():
        if node1 == node2:
            x, y = pos[node1]
            label_pos_adjusted[(node1, node2)] = (x, y + 0.09)
        else:
            label_pos_adjusted[(node1, node2)] = pos[node2]

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_weight='normal', font_size=8)
    plt.show()


def query(graph, query_string):
    elements = query_string.split()
    nodes = [e for e in elements if e[0].isupper()]
    relationships = [e for e in elements if e[0].islower()]

    if len(nodes) == 1 and not relationships:  # Node1
        # Return all nodes that have a direct relationship with the specified node
        return list(graph.predecessors(nodes[0]))
        #return list(graph.successors(nodes[0]))

    elif len(nodes) == 2 and not relationships:  # Node1 Node2
        # Check for direct relationship
        if graph.has_edge(nodes[0], nodes[1]):
            return graph[nodes[0]][nodes[1]].get('relationship')
        # Check for transitive relationship
        elif nx.has_path(graph, nodes[0], nodes[1]):
            path = nx.shortest_path(graph, source=nodes[0], target=nodes[1])
            transitive_relationships = []
            for i in range(len(path) - 1):
                transitive_relationships.append(graph[path[i]][path[i + 1]].get('relationship'))
            return transitive_relationships, path
        else:
            return None
    elif len(nodes) == 1 and relationships:  # Node1 relationship {Parent Node}
        # Return all nodes that have a direct or transitive relationship with the specified node and the specified relationship
        descendants = nx.descendants(graph, nodes[0])
        return [node for node in descendants if relationships[0] in [graph.edges[n, node].get('relationship') for n in nx.shortest_path(graph, nodes[0], node)[:-1] if graph.has_edge(n, node)]]

    elif len(nodes) == 2 and relationships:  # Node1 relationship Node2
        # Check for direct or transitive relationship with the specified relationship
        paths = nx.all_simple_paths(graph, nodes[0], nodes[1])
        result = any(relationships[0] in [graph.edges[node, path[path.index(node) + 1]].get('relationship') for node in path[:-1] if graph.has_edge(node, path[path.index(node) + 1])] for path in paths)

        #Rules exceptions
        birds_cant_fly = ["Penguin", "Flamingo", "Chicken"]
        exception_mammals = ["Whale", "Seals"]
        if nodes[0] in birds_cant_fly and nodes[1] == 'Fly':
            return False
        elif nodes[0] in exception_mammals and nodes[1] in ["Land", "Leg"]:
            return False
        else:
            return result
    else:
        return None



def read_from_csv(file_name, graph):
    df = pd.read_csv(file_name)

    # Add nodes
    for node in df['Node'].unique():
        graph.add_node(node)

    # Add relationships
    for _, row in df.iterrows():
        graph.add_edge(row['Node'], row['Connected_Node'], relationship=row['Relationship'])

G = nx.DiGraph()  # Create a directed graph

while True:
    print("\nOptions:")
    print("1. Add Node")
    print("2. Remove Node")
    print("3. Add Relationship")
    print("4. Remove Relationship")
    print("5. Query")
    print("6. Visualize Graph")
    print("7. Load from CSV")
    print("8. Exit")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        node = input("Enter node name: ")
        if node not in G:
            G.add_node(node)
        else:
            print(f"Node {node} already exist")
    elif choice == 2:
        node = input("Enter node name: ")
        if node in G:
            G.remove_node(node)
            print(f"Node {node} removed successfully.")
        else:
            print(f"Node {node} does not exist.")
    elif choice == 3:
        node1 = input("Enter first node: ")
        node2 = input("Enter second node: ")
        relationship = input("Enter relationship: ")
        G.add_edge(node1, node2, relationship=relationship)
    elif choice == 4:
        node1 = input("Enter first node: ")
        node2 = input("Enter second node: ")
        if G.has_edge(node1, node2):
            G.remove_edge(node1, node2)
            print(f"Relationship between {node1} and {node2} removed successfully.")
        else:
            print(f"No relationship exists between {node1} and {node2}.")
    elif choice == 5:
        query_string = input("Enter query (e.g., 'Node1 relationship Node2'): ")
        elements = query_string.split()
        if elements[0] not in G: print(f"Cannot query because {elements[0]} doesn't exist")
        if elements[-1] not in G: print(f"Cannot query because {elements[-1]} doesn't exist")

        result = query(G, query_string)
        print(result)
    elif choice == 6:
        visualize_graph(G)
    elif choice == 7:
        file_name = input("Enter CSV file name: ")
        read_from_csv(file_name, G)
    elif choice == 8:
        break