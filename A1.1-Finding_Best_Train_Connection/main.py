import pandas as pd
import networkx as nx

def parse_time(time_str):
    if isinstance(time_str, str):
        time_str = time_str.replace("'", "")  # Remove surrounding quotes
        return pd.to_datetime(time_str, format='%H:%M:%S').time()
    else:
        return pd.NaT

def calculate_time_difference(start_time, end_time):
    start_dt = pd.Timestamp.combine(pd.Timestamp.today(), start_time)
    end_dt = pd.Timestamp.combine(pd.Timestamp.today(), end_time)
    if end_dt < start_dt:
        end_dt += pd.Timedelta(days=1)
    return (end_dt - start_dt).total_seconds() 

def create_graph(schedule_df, weight_type):
    schedule_df['Train No.'] = schedule_df['Train No.'].astype(str).str.replace("'", "").astype(int)
    schedule_df['Departure time'] = schedule_df['Departure time'].astype(str).apply(parse_time)
    schedule_df['Arrival time'] = schedule_df['Arrival time'].astype(str).apply(parse_time)

    G = nx.DiGraph()
    for train in schedule_df['Train No.'].unique():
        train_data = schedule_df[schedule_df['Train No.'] == train]
        for i in range(len(train_data) - 1):
            node1 = train_data.iloc[i]['station Code'].strip()
            node2 = train_data.iloc[i + 1]['station Code'].strip()
            
            islno_weight = abs(train_data.iloc[i]['islno'] - train_data.iloc[i + 1]['islno'])
            
            dep_time = train_data.iloc[i]['Departure time']
            arr_time = train_data.iloc[i + 1]['Arrival time']
            time_weight = calculate_time_difference(dep_time, arr_time)
            
            if weight_type == 'islno_weight':
                weight = islno_weight
            elif weight_type == 'time_weight':
                weight = time_weight
            elif weight_type == 'price_weight':
                if islno_weight == 1:
                    weight = 1
                else:
                    weight = min(10, islno_weight)
            else:
                weight = islno_weight
                
            G.add_edge(node1, node2, weight=weight, train_no=train, start=train_data.iloc[i]['islno'], end=train_data.iloc[i + 1]['islno'], arr_time=arr_time)
    return G

def heuristic(n1, n2, node_positions):
    x1, y1 = node_positions[n1]
    x2, y2 = node_positions[n2]
    return abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance

def process_problems(problem_df, G1, G2, G3, G4, G5, G6, G7, G8):
    problems_df = problem_df[((problem_df['CostFunction'].apply(lambda x: x.startswith('arrivaltime'))) | 
                              (problem_df['CostFunction'].isin(['stops', 'traveltime', 'price']))) & 
                             ((problem_df['Schedule'] == 'mini-schedule.csv') | 
                              (problem_df['Schedule'] == 'schedule.csv'))]
    
    output_data = []

    # Generate node positions for heuristic calculation
    unique_stations = set(schedule_df_1['station Code'].unique()).union(set(schedule_df_2['station Code'].unique()))
    node_positions = {station.strip(): (idx % 10, idx // 10) for idx, station in enumerate(unique_stations)}

    for index, row in problems_df.iterrows():
        source_node = row['FromStation'].strip()
        target_node = row['ToStation'].strip()
        
        if row['Schedule'] == 'mini-schedule.csv':
            if row['CostFunction'] == 'stops':
                G = G1
            elif row['CostFunction'] == 'traveltime':
                G = G2
            elif row['CostFunction'] == 'price':
                G = G3
            elif row['CostFunction'].startswith('arrivaltime'):
                G = G7
        else:
            if row['CostFunction'] == 'stops':
                G = G4
            elif row['CostFunction'] == 'traveltime':
                G = G5
            elif row['CostFunction'] == 'price':
                G = G6
            elif row['CostFunction'].startswith('arrivaltime'):
                G = G8

        weight = 'weight'

        if row['CostFunction'].startswith('arrivaltime'):
            arrival_time1_str = row['CostFunction'].replace('arrivaltime', '').strip()
            arrival_time1 = pd.to_datetime(arrival_time1_str, format='%H:%M:%S').time()

            try:
                shortest_path = nx.astar_path(G, source=source_node, target=target_node, heuristic=lambda n1, n2: heuristic(n1, n2, node_positions), weight=weight)
                connection = []
                total_cost = None

                for i in range(len(shortest_path) - 1):
                    edge = G[shortest_path[i]][shortest_path[i + 1]]
                    train_no = edge['train_no']
                    start_islno = edge['start']
                    end_islno = edge['end']
                    connection.append(f"{train_no} : {start_islno} -> {end_islno}")

                    arrival_time2 = pd.to_datetime(str(edge['arr_time'])).time()
                    if arrival_time1 < arrival_time2:
                        total_cost = f"1:{edge['arr_time'].strftime('%H:%M:%S')}"
                    else:
                        total_cost = f"2:{edge['arr_time'].strftime('%H:%M:%S')}"

                if connection:
                    output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': ' ; '.join(connection), 'Cost': total_cost})
                else:
                    output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': 'No path found', 'Cost': 'N/A'})
            except nx.NetworkXNoPath:
                output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': 'No path found', 'Cost': 'N/A'})
            except KeyError as e:
                output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': f'Error: {str(e)}', 'Cost': 'N/A'})

        else:
            try:
                shortest_path = nx.dijkstra_path(G, source=source_node, target=target_node, weight=weight)
                cost = nx.dijkstra_path_length(G, source=source_node, target=target_node, weight=weight)
                connection = []

                for i in range(len(shortest_path) - 1):
                    edge = G[shortest_path[i]][shortest_path[i + 1]]
                    train_no = edge['train_no']
                    start_islno = edge['start']
                    end_islno = edge['end']
                    connection.append(f"{train_no} : {start_islno} -> {end_islno}")
                    
                if connection:
                    output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': ' ; '.join(connection), 'Cost': int(cost)})
                else:
                    output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': 'No path found', 'Cost': 'N/A'})
            except nx.NetworkXNoPath:
                output_data.append({'ProblemNo': row['ProblemNo'], 'Connection': 'No path found', 'Cost': 'N/A'})

    output_df = pd.DataFrame(output_data)
    output_df.to_csv("C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.1/solution.csv", index=False)

# Read CSV files
schedule_df_1 = pd.read_csv("C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.1/mini-schedule.csv")
schedule_df_2 = pd.read_csv("C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.1/schedule.csv")
problem_df = pd.read_csv("C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.1/problems.csv")

G1 = create_graph(schedule_df_1, 'islno_weight')
G2 = create_graph(schedule_df_1, 'time_weight')
G3 = create_graph(schedule_df_1, 'price_weight')

G4 = create_graph(schedule_df_2, 'islno_weight')
G5 = create_graph(schedule_df_2, 'time_weight')
G6 = create_graph(schedule_df_2, 'price_weight')

G7 = create_graph(schedule_df_1, 'islno_weight')
G8 = create_graph(schedule_df_2, 'islno_weight')

process_problems(problem_df, G1, G2, G3, G4, G5, G6, G7, G8)