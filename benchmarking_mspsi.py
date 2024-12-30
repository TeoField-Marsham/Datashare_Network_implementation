# SPEED TEST FOR MSPSI

# To switch between SMALL and LARGE dataset tests, change the `TEST_TYPE` variable below.
TEST_TYPE = 'LARGE' # Options: 'SMALL' or 'LARGE'

import time
import mspsi
import random
import string

def server_setup():
    if TEST_TYPE == 'LARGE':
        return server_setup_LARGE_DATASET() 
    elif TEST_TYPE == 'SMALL':
        return server_setup_SMALL_DATASET()
    else:
        raise ValueError("Invalid TEST_TYPE. Please only enter 'LARGE' or 'SMALL'.")

def client_setup():
    if TEST_TYPE == 'LARGE':
        return client_setup_LARGE_DATASET() 
    elif TEST_TYPE == 'SMALL':
        return client_setup_SMALL_DATASET()
    else:
        raise ValueError("Invalid TEST_TYPE. Please only enter 'LARGE' or 'SMALL'.")

def generate_large_keyword_pool(num_keywords):
    # Creates a pool of random 5-letter keywords
    keyword_pool = []
    for _ in range(num_keywords):
        kwd = ''.join(random.choices(string.ascii_lowercase, k=5))
        keyword_pool.append(kwd)
    return keyword_pool

def server_setup_LARGE_DATASET():
    random.seed(42) # Ensures that the pool and search keywords are always the same
    keyword_pool = generate_large_keyword_pool(100)

    num_docs = 30
    keywords_per_doc = 10

    server_documents = {}
    for doc_id_num in range(1, num_docs+1):
        doc_id = f"doc{doc_id_num}"
        # Choose random keywords from the pool
        doc_keywords = random.choices(keyword_pool, k=keywords_per_doc)
        server_documents[doc_id] = doc_keywords

    # Hash/encrypt server's keywords per document
    server_elements_per_doc = {
        doc_id: [mspsi.hash_to_int(kwd) for kwd in keywords]
        for doc_id, keywords in server_documents.items()
    }
    return server_elements_per_doc

def client_setup_LARGE_DATASET():
    random.seed(42) # Ensures that the pool and search keywords are always the same
    keyword_pool = generate_large_keyword_pool(100)

    # Pick 10 keywords to search for
    client_keywords = random.sample(keyword_pool, 10)

    # Assign IDs to the keywords
    client_keyword_ids = list(range(1, len(client_keywords)+1))

    # Hash/encrypt client's keywords
    client_elements = []
    client_element_id_map = {}
    for idx, kwd in zip(client_keyword_ids, client_keywords):
        elem = mspsi.hash_to_int(kwd)
        client_elements.append(elem)
        if elem not in client_element_id_map:
            client_element_id_map[elem] = []
        client_element_id_map[elem].append(idx)

    return client_elements, client_element_id_map

def server_setup_SMALL_DATASET():
    return mspsi.server_setup()

def client_setup_SMALL_DATASET():
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


# Begin total timing
total_start_time = time.time()

server_elements_per_doc = server_setup()
client_elements, client_element_id_map = client_setup()

# Measure the time taken by client_transform()
start_time = time.time()
client_secret, client_transformed_elements = mspsi.client_transform(client_elements, client_element_id_map)
end_time = time.time()
client_transform_time = end_time - start_time

# Measure the time taken by server_transform()
start_time = time.time()
server_secret, tag_collections_per_doc = mspsi.server_transform(server_elements_per_doc)
end_time = time.time()
server_transform_time = end_time - start_time

"""Client sends client_transformed_elements to server"""

# Measure the time taken by server_process()
start_time = time.time()
server_data = mspsi.server_process(server_secret, tag_collections_per_doc, client_transformed_elements)
end_time = time.time()
server_process_time = end_time - start_time

"""Server sends tag_collection and client_elements_server to client"""

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
print(f"Time taken by server_transform(): {server_transform_time * 1000:.5f} milliseconds")
print(f"Time taken by server_process(): {server_process_time * 1000:.5f} milliseconds")
print(f"Time taken by client_compute_intersection(): {client_compute_intersection_time * 1000:.5f} milliseconds")
print(f"Total time taken: {total_time * 1000:.5f} milliseconds")
print("\n")