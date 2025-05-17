import shutil
from utils import *
import requests as re
import xml.etree.ElementTree as ET
import logging
import subprocess
import os
import sys
import random
import psutil
import signal
import time
from collections import deque

def execute_query(query_string, result_type):
    server_url = "http://localhost:9999/blazegraph/namespace/kb/sparql"
    
    # Sending the query to the server
    response = re.get(server_url, params={"query": query_string})
    
    # Removing unwanted XML namespace
    cleaned_xml = response.text.replace("xmlns='http://www.w3.org/2005/sparql-results#'", "")
    
    # Parsing the XML response
    parsed_xml = ET.fromstring(cleaned_xml)
    results = []

    # Extracting data based on the result type
    for item in parsed_xml.findall("results/result"):
        if result_type == "top-authors":
            author_name = item.find("binding[@name='author']/uri").text
            author_count = item.find("binding[@name='count']/literal").text
            results.append((author_name, author_count))
        else:
            result_value = item.find("binding/uri").text
            results.append(result_value)
    
    return results


def construct_keyword_query(problem):
    query = """
    PREFIX info: <https://zbmath.org/infos#>
    SELECT DISTINCT ?keyword
    WHERE 
    {   
        ?record info:author <""" + problem.queries[0] + """>. 
        ?record info:keyword ?keyword.
    }
    """
    problem.query = query
    problem.solutions = execute_query(query, problem.type)
    return problem

def build_classification_intersection_query(problem):
    classifications = " ".join([f"?record info:classification ?class{i}." for i in range(len(problem.queries))])
    filters = " ".join([f"FILTER(STRSTARTS(STR(?class{i}), \"{class_}\"))" for i, class_ in enumerate(problem.queries)])

    query = f"""
    PREFIX info: <https://zbmath.org/infos#>
    SELECT DISTINCT ?record
    WHERE 
    {{
    {classifications}
    {filters}
    }}
    """
    problem.query = query
    problem.solutions = execute_query(query, problem.type)
    return problem

def create_top_authors_query(problem):
    query = f"""
    PREFIX info: <https://zbmath.org/infos#>
    SELECT ?author (COUNT(DISTINCT ?record) as ?count)
    WHERE 
    {{
        ?record info:keyword <{problem.queries[0]}>.
        ?record info:author ?author.
        ?record info:year ?year.
        FILTER(xsd:integer(?year) > {problem.after} && xsd:integer(?year) < {problem.before})
    }}
    GROUP BY ?author
    ORDER BY DESC(?count)
    LIMIT 10
    """
    problem.query = query
    problem.solutions = execute_query(query, problem.type)
    return problem

def check_process(pName):
    for i in psutil.process_iter():
        try:
            if pName.lower() in i.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def find_Process_id(pName):
    list1 = []
    for i in psutil.process_iter():
        try:
            pinfo = i.as_dict(attrs=['pid', 'name', 'create_time'])
            if pName.lower() in pinfo['name'].lower():
                list1.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return list1

def kill_java_process():
    for i in psutil.process_iter(['pid', 'name']):
        if 'java' in i.info['name'].lower():
            try:
                i.terminate()
                i.wait(timeout=10)
            except psutil.NoSuchProcess:
                pass
            except psutil.TimeoutExpired:
                i.kill()

def setup_database(file):
    print("Initializing database...")
    blazegraph_jar = "blazegraph.jar"
    
    print("Starting Blazegraph server...")
    process = subprocess.Popen(['java', '-server', '-Xmx8g', '-jar', blazegraph_jar], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    query_server = "http://localhost:9999/blazegraph/"
    for i in range(60):  # Wait up to 60 seconds
        time.sleep(1)
        try:
            response = re.get(query_server, timeout=5)
            if response.status_code == 200:
                print(f"Blazegraph server is ready.")
                break
        except re.exceptions.RequestException:
            pass
    else:
        print("Failed to start Blazegraph server")
        return

    print("Preparing for bulk loading...")
    bulk_journal_file = "bulk_load.jnl"
    if os.path.exists(bulk_journal_file):
        os.remove(bulk_journal_file)

    abs_file_path = os.path.abspath(file)
    if not os.path.exists(abs_file_path):
        print(f"Error: RDF file not found at {abs_file_path}")
        return

    input_size = os.path.getsize(abs_file_path)
    bulk_load_command = f"java -cp blazegraph.jar com.bigdata.rdf.store.DataLoader -namespace kb -defaultGraph http://example.org bulk_load.properties {abs_file_path}"
    
    print("Starting bulk load process...")
    start_time = time.time()
    try:
        process = subprocess.Popen(bulk_load_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error during bulk load. Return code: {process.returncode}")
            print("Error output:")
            print(stderr)
            return

        load_time = time.time() - start_time
        stmts_added = int(stdout.split("Load:")[1].split("stmts added")[0].strip())
        print(f"Bulk load complete. {stmts_added} statements added in {load_time:.2f} seconds.")

    except Exception as e:
        print(f"Error during bulk load: {e}")
        return

    print("Restarting Blazegraph server with new data...")
    kill_java_process()
    shutil.copy(bulk_journal_file, "blazegraph.jnl")
    process = subprocess.Popen(['java', '-server', '-Xmx8g', '-jar', blazegraph_jar], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for i in range(60):  # Wait up to 60 seconds
        time.sleep(1)
        try:
            response = re.get(query_server, timeout=5)
            if response.status_code == 200:
                print("Blazegraph server restarted successfully.")
                break
        except re.exceptions.RequestException:
            pass
    else:
        print("Failed to restart Blazegraph server")
        return

    print("Verifying loaded data...")
    try:
        check_query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        response = re.get(query_server + "namespace/kb/sparql", params={"query": check_query}, timeout=30)
        if response.status_code == 200:
            count = int(response.text.split("<literal")[1].split(">")[1].split("<")[0])
            print(f"Number of triples in the database: {count}")
        else:
            print("Failed to verify loaded data.")
    except Exception as e:
        print(f"Error verifying loaded data: {str(e)}")

    print("Database initialization complete.")

def shutdown_database():
    if check_process("java"):
        infos = find_Process_id("java")
        for info in infos:
            try:
                os.kill(info['pid'], signal.SIGTERM)
                print(f"Sent SIGTERM to process ID {info['pid']}")
            except ProcessLookupError:
                print(f"Process ID {info['pid']} no longer exists")
            except PermissionError:
                print(f"No permission to terminate process ID {info['pid']}")

def process_problems(problem_file, solution_filename):
    # Parse the problem file into a list of problems
    problems = parse_problem_xml(problem_file)

    # Iterate over each problem and process based on its type
    for problem in problems:
        if problem.type == "top-authors":
            problem = create_top_authors_query(problem)
        elif problem.type == "keywords":
            problem = construct_keyword_query(problem)
        elif problem.type == "msc-intersection":
            problem = build_classification_intersection_query(problem)

    # Generate the solution XML file based on the processed problems
    generate_solution_xml(problems, solution_filename)

    
def get_file_names(dataset, problem_file):
    dataset_name = os.path.splitext(os.path.splitext(os.path.basename(dataset))[0])[0]  # Remove both .xml and .bz2 extensions
    problem_name = os.path.splitext(os.path.basename(problem_file))[0]
    
    if dataset_name == 'mini-dataset':
        rdf_filename = 'mini-rdfdata.rdf'
    elif dataset_name == 'big-dataset':
        rdf_filename = 'big-rdfdata.rdf'
    else:
        raise ValueError(f"Unknown dataset: {dataset}")
    
    if problem_name.startswith('example-problems'):
        solution_filename = f'example_solutions_{dataset_name.split("-")[0]}.xml'
    elif problem_name.startswith('problems'):
        solution_filename = f'solutions_{dataset_name.split("-")[0]}.xml'
    else:
        raise ValueError(f"Unknown problem file: {problem_file}")
    
    return rdf_filename, solution_filename

def process_command_line_args():
    args = sys.argv
    if len(args) < 4:
        return

    dataset = next((args[i+1] for i, arg in enumerate(args) if arg == '-b'), None)
    problem_file = next((args[i+1] for i, arg in enumerate(args) if arg == '-r'), None)
    force_regenerate = '-f' in args

    if not dataset or not problem_file:
        print("Missing dataset or problem file argument")
        return

    rdf_filename, solution_filename = get_file_names(dataset, problem_file)
    print(f"Using RDF filename: {rdf_filename}")
    print(f"Using solution filename: {solution_filename}")

    if not os.path.exists(rdf_filename) or force_regenerate:
        print(f"Generating {rdf_filename}...")
        start_time = time.time()
        buildRdfDataFile(dataset, rdf_filename)
        end_time = time.time()
        print(f"RDF file created in {end_time - start_time:.2f} seconds")
    else:
        print(f"Using existing RDF file: {rdf_filename}")

    if "-w" in args:
        start_time = time.time()
        setup_database(rdf_filename)
        end_time = time.time()
        print(f"Database initialization time: {end_time - start_time:.2f} seconds")

    if "-r" in args:
        print("Executing queries...")
        start_time = time.time()
        process_problems(problem_file, solution_filename)
        end_time = time.time()
        print(f"Query execution time: {end_time - start_time:.2f} seconds")
        print("Terminating database...")
        shutdown_database()

    print("Process completed.")

if __name__ == "__main__":
    process_command_line_args()
