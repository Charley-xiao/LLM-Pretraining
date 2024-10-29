import os
import ast
import networkx as nx
import matplotlib.pyplot as plt

def get_python_files(repo_path):
    """ Recursively collect all Python files in the repository """
    python_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def parse_imports(file_path):
    """ Parse import statements from a Python file using AST """
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    tree = ast.parse(file_content)
    imports = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
    
    return imports

def build_dependency_graph(repo_path):
    """ Build a dependency graph for the Python files in the repository """
    graph = nx.DiGraph()
    
    python_files = get_python_files(repo_path)
    
    for file in python_files:
        file_node = os.path.relpath(file, repo_path)  # Relative path for cleaner graph nodes
        graph.add_node(file_node)
        imports = parse_imports(file)
        
        for imp in imports:
            # Adding an edge if the import exists in the repo
            imported_file = find_file_by_module(imp, repo_path)
            if imported_file:
                graph.add_edge(file_node, imported_file)
    
    return graph

def find_file_by_module(module_name, repo_path):
    """ Helper function to map import to a .py file in the repo """
    module_path = module_name.replace('.', '/') + '.py'
    for root, dirs, files in os.walk(repo_path):
        if module_path in files:
            return os.path.relpath(os.path.join(root, module_path), repo_path)
    return None

def visualize_dependency_graph(graph):
    """ Visualize the dependency graph using networkx and matplotlib """
    plt.figure(figsize=(16, 12)) 
    pos = nx.spring_layout(graph, k=0.5, iterations=100)  
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=8, font_weight="bold", arrows=True, alpha=0.7)
    
    nx.draw_networkx_edges(graph, pos, edge_color='gray', alpha=0.5, arrows=True)
    
    plt.title("Python Repository Dependency Graph")
    plt.show()


def show_stats(graph):
    """ Show basic statistics about the dependency graph """
    print(f"Number of nodes: {graph.number_of_nodes()}")
    print(f"Number of edges: {graph.number_of_edges()}")
    print(f"Is cyclic: {nx.is_directed_acyclic_graph(graph)}")
    # Isoalted nodes
    isolated_nodes = list(nx.isolates(graph))
    if isolated_nodes:
        print(f"Found {len(isolated_nodes)} isolated nodes:")
        for node in isolated_nodes:
            print(node)
    else:
        print("No isolated nodes found")

    print("Graph edges:")
    for edge in graph.edges:
        # Convert \ to / for better readability
        u = edge[0].replace("\\", "/")
        v = edge[1].replace("\\", "/")
        print(f"{u} {v}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Python Repository Dependency Analyzer")
    parser.add_argument("--repo_path", type=str, help="Path to the Python repository")
    args = parser.parse_args()

    repo_path = args.repo_path
    
    # Build the dependency graph
    dep_graph = build_dependency_graph(repo_path)

    show_stats(dep_graph)
    
    # Visualize the graph
    visualize_dependency_graph(dep_graph)
