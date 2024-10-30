import os
import ast
import networkx as nx
import matplotlib.pyplot as plt
import re
import pickle 


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
    
    def visualize_dependency_graph(self):
        """ Visualize the dependency graph using networkx and matplotlib """
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=2000, font_size=10, node_color='skyblue', edge_color='gray')
        plt.show()


class PythonDependencyAnalyzer(DependencyAnalyzer):
    def __init__(self, repo_path):
        super().__init__(repo_path)

    def get_files(self):
        """ Recursively collect all Python files in the repository """
        python_files = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
    
    def parse_imports(self, file_path):
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
    
    def build_dependency_graph(self):
        """ Build a dependency graph for the Python files in the repository """
        python_files = self.get_files()
        
        for file in python_files:
            file_node = os.path.relpath(file, self.repo_path)
            self.graph.add_node(file_node)
            imports = self.parse_imports(file)

            for imp in imports:
                imported_file = self.find_file_by_module(imp)
                if imported_file:
                    self.graph.add_edge(file_node, imported_file)

    def find_file_by_module(self, module_name):
        """ Helper function to map import to a .py file in the repo """
        module_path = module_name.replace('.', '/') + '.py'
        for root, dirs, files in os.walk(self.repo_path):
            if module_path in files:
                return os.path.relpath(os.path.join(root, module_path), self.repo_path)
        return None
    

class JavaDependencyAnalyzer(DependencyAnalyzer):
    def __init__(self, repo_path):
        super().__init__(repo_path)

    def get_files(self):
        """ Recursively collect all Java files in the repository """
        java_files = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        return java_files
    
    def parse_imports(self, file_path):
        """ Parse import statements from a Java file """
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        imports = set(re.findall(r'^import\s+([\w\.]+);', file_content, re.MULTILINE))
        return imports
    
    def build_dependency_graph(self):
        """ Build a dependency graph for the Java files in the repository """
        java_files = self.get_files()
        
        for file in java_files:
            file_node = os.path.relpath(file, self.repo_path)
            self.graph.add_node(file_node)
            imports = self.parse_imports(file)

            for imp in imports:
                imported_file = self.find_file_by_module(imp)
                if imported_file:
                    self.graph.add_edge(file_node, imported_file)

    def find_file_by_module(self, module_name):
        """ Helper function to map import to a .java file in the repo """
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