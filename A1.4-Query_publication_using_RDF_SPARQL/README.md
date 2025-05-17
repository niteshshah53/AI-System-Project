# Assignment 4: Query publication data from zbMATH

## Prerequisites
- Python 3.7 or higher

## Required Libraries
- requests
- psutil
- signal

Install dependencies using pip:
pip install requests psutil

## Running the Code

### Basic Usage

python main.py -b <dataset.xml.bz2> [-f] -w -r <problems.xml>

### Flags
- `-b`: Specify the input dataset (XML.bz2 file)
- `-f`: Force regeneration of RDF data (optional)
- `-w`: Update Blazegraph with RDF data
- `-r`: Run queries using the specified problem file

### Examples

1. Normal run (uses existing RDF file if available):
python main.py -b mini-dataset.xml.bz2 -w -r example-problems-mini.xml
2. Force RDF regeneration:
python main.py -b mini-dataset.xml.bz2 -f -w -r example-problems-mini.xml
3. Run with big dataset:
python main.py -b big-dataset.xml.bz2 -w -r example-problems-big.xml

## Output
- The script will generate a solution XML file (e.g., `example_solutions_mini.xml` or `solutions_big.xml`) in the same directory.

## Verifying Solutions
You can use `verify.py` to check your solutions for the example problems:

1. For mini dataset:
python verify.py mini path/to/your/example-solutions-mini.xml
2. For big dataset:
python verify.py big path/to/your/example-solutions-big.xml

## Troubleshooting
- If you encounter issues with Blazegraph server startup or connection, the script will attempt to restart the server and retry queries.
- Check the console output for any error messages or warnings.

## Notes
- The script uses Blazegraph for storing and querying RDF data. Make sure `blazegraph.jar` is in the same directory as the script.
- For large datasets, ensure you have sufficient memory and disk space available.
- The bulk loading process for large datasets may take a considerable amount of time.