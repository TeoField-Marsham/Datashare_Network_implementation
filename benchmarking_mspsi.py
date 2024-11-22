# SPEED TEST FOR MSPSI

import time
import mspsi

def client_setup_override():
    # Enter test keywords
    client_keywords = ['apple', 'banana']

    # Assign IDs to the keywords
    client_keyword_ids = list(range(1, len(client_keywords)+1))

    # Hash/encrypt client's keywords to integers and map them to IDs
    client_elements = []
    client_element_id_map = {}
    for idx, kwd in zip(client_keyword_ids, client_keywords):
        elem = mspsi.hash_to_int(kwd)
        client_elements.append(elem)
        if elem not in client_element_id_map:
            client_element_id_map[elem] = []
        client_element_id_map[elem].append(idx)

    return client_elements, client_element_id_map

# Override the client_setup function in mspsi.py
mspsi.client_setup = client_setup_override

# Begin total timing
total_start_time = time.time()

server_elements_per_doc = mspsi.server_setup()
client_elements, client_element_id_map = mspsi.client_setup()

# Measure the time taken by client_transform()
start_time = time.time()
client_secret, client_transformed_elements = mspsi.client_transform(client_elements, client_element_id_map)
end_time = time.time()
client_transform_time = end_time - start_time

"""Client sends client_transformed_elements to server"""

# Measure the time taken by server_process()
start_time = time.time()
server_data = mspsi.server_process(server_elements_per_doc, client_transformed_elements)
end_time = time.time()
server_process_time = end_time - start_time

"""Server sends server_transformed_elements and client_elements_server to client"""

# Measure the time taken by client_compute_intersection()
start_time = time.time()
counts_per_doc = mspsi.client_compute_intersection(client_secret, server_data)
end_time = time.time()
client_compute_intersection_time = end_time - start_time

# End total timing
total_end_time = time.time()
total_time = total_end_time - total_start_time

print("\n")
for doc_id, ids in counts_per_doc:
    ids = sorted(ids)
    if ids:
        ids_str = ', '.join(map(str, ids))
        print(f"Document '{doc_id}' has matching keyword IDs: {ids_str}.")
    else:
        print(f"Document '{doc_id}' has no matching keywords.")

print("\n")
print(f"Time taken by client_transform(): {client_transform_time * 1000:.5f} milliseconds")
print(f"Time taken by server_process(): {server_process_time * 1000:.5f} milliseconds")
print(f"Time taken by client_compute_intersection(): {client_compute_intersection_time * 1000:.5f} milliseconds")
print(f"Total time taken: {total_time * 1000:.5f} milliseconds")
print("\n")