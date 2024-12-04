import os
import ast
import networkx as nx
import matplotlib.pyplot as plt
import re
import pickle 
from concurrent.futures import ThreadPoolExecutor, as_completed


class DependencyAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.graph = nx.DiGraph()

    def get_files(self):
        """ Recursively collect all files in the repository """
        raise NotImplementedError
    
    def parse_imports(self, file_path):
        """ Parse import statements from a file using AST """
        raise NotImplementedError
    
    def build_dependency_graph(self):
        """ Build a dependency graph for the files in the repository """
        raise NotImplementedError
    
    def find_file_by_module(self, module_name):
        """ Helper function to map import to a file in the repo """
        raise NotImplementedError
    
    def visualize_dependency_graph(self, save_path=None):
        """ Visualize the dependency graph using networkx and matplotlib """
        plt.figure(figsize=(32, 24))
        pos = nx.spring_layout(self.graph, iterations=100)
        nx.draw(self.graph, pos, with_labels=True, node_size=2000, font_size=10, node_color='skyblue', edge_color='black', alpha=0.7)
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        plt.close()


class PythonDependencyAnalyzer(DependencyAnalyzer):
    def __init__(self, repo_path):
        super().__init__(repo_path)
        self.graph = nx.DiGraph()

    def get_files(self):
        """Recursively collect all Python files in the repository"""
        python_files = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def parse_imports(self, file_path):
        """Parse import statements from a Python file using AST"""
        print(f"Parsing file {file_path}")
        with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
            file_content = file.read()
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            print(f"Syntax error parsing file {file_path}: {e}. Returning empty set.")
            return set()
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)

        return imports

    def process_file(self, file):
        """Process a single file to extract dependencies"""
        file_node = os.path.relpath(file, self.repo_path)
        imports = self.parse_imports(file)
        edges = []
        for imp in imports:
            if imp == '__future__' or imp is None:
                continue
            imported_file = self.find_file_by_module(imp)
            if imported_file:
                edges.append((file_node, imported_file))
        return file_node, edges

    def build_dependency_graph(self):
        """Build a dependency graph for the Python files in the repository"""
        python_files = self.get_files()
        print(f"Found {len(python_files)} Python files in the repository")

        nodes = []
        edges = []

        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(self.process_file, file): file for file in python_files}

            for future in as_completed(future_to_file):
                try:
                    file_node, file_edges = future.result()
                    nodes.append(file_node)
                    edges.extend(file_edges)
                except Exception as e:
                    print(f"Error processing file {future_to_file[future]}: {e}")

        # Build the graph
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)

    def find_file_by_module(self, module_name):
        """Helper function to map import to a .py file in the repo"""
        module_path = module_name.replace('.', '/') + '.py'
        for root, dirs, files in os.walk(self.repo_path):
            if module_path in files:
                return os.path.relpath(os.path.join(root, module_path), self.repo_path)
        return None
    

class JavaDependencyAnalyzer(DependencyAnalyzer):
    def __init__(self, repo_path):
        super().__init__(repo_path)
        self.graph = nx.DiGraph()

    def get_files(self):
        """Recursively collect all Java files in the repository"""
        java_files = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        return java_files

    def parse_imports(self, file_path):
        """Parse import statements from a Java file"""
        print(f"Parsing file {file_path}")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            file_content = file.read()

        # Use regex to extract import statements
        imports = set(re.findall(r'^import\s+([\w\.]+);', file_content, re.MULTILINE))
        return imports

    def process_file(self, file):
        """Process a single Java file to extract dependencies"""
        file_node = os.path.relpath(file, self.repo_path)
        imports = self.parse_imports(file)
        edges = []
        for imp in imports:
            if imp is None:
                continue
            imported_file = self.find_file_by_module(imp)
            if imported_file:
                edges.append((file_node, imported_file))
        return file_node, edges

    def build_dependency_graph(self):
        """Build a dependency graph for the Java files in the repository"""
        java_files = self.get_files()
        print(f"Found {len(java_files)} Java files in the repository")

        nodes = []
        edges = []

        with ThreadPoolExecutor() as executor:
            # Submit tasks to process each file
            future_to_file = {executor.submit(self.process_file, file): file for file in java_files}

            for future in as_completed(future_to_file):
                try:
                    file_node, file_edges = future.result()
                    nodes.append(file_node)
                    edges.extend(file_edges)
                except Exception as e:
                    print(f"Error processing file {future_to_file[future]}: {e}")

        # Build the graph
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)

    def find_file_by_module(self, module_name):
        """Helper function to map import to a .java file in the repo"""
        module_path = module_name.replace('.', '/') + '.java'
        for root, dirs, files in os.walk(self.repo_path):
            if module_path in files:
                return os.path.relpath(os.path.join(root, module_path), self.repo_path)

        return None
    

def get_dependency_graph(repo_path, language) -> nx.DiGraph:
    if language == 'python':
        analyzer = PythonDependencyAnalyzer(repo_path)
    elif language == 'java':
        analyzer = JavaDependencyAnalyzer(repo_path)
    else:
        raise ValueError("Unsupported language for dependency analysis")
    
    analyzer.build_dependency_graph()
    return analyzer.graph


def save_dependency_graph(graph, output_file):
    with open(output_file, 'wb') as f:
        pickle.dump(graph, f)


def visualize_graph(graph, save_path=None):
    """ Visualize a given graph using networkx and matplotlib """
    plt.figure(figsize=(32, 24))
    pos = nx.spring_layout(graph, iterations=100)
    nx.draw(graph, pos, with_labels=True, node_size=2000, font_size=10, node_color='skyblue', edge_color='black', alpha=0.7)
    if save_path:
        if not os.path.exists(save_path):
            plt.savefig(save_path)
        else:
            print(f"File {save_path} already exists. Skipping save.")
    else:
        plt.show()
    plt.close()