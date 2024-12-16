# SPEED TEST FOR PSI

import time
import psi
import random
import string

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

    keywords_num = 300

    server_keywords = {'doc': random.choices(keyword_pool, k=keywords_num)}

    # Hash/encrypt server's keywords
    server_elements = {doc_id: [psi.hash_to_int(kwd) for kwd in keywords]
                        for doc_id, keywords in server_keywords.items()}

    return server_elements

def client_setup_LARGE_DATASET():
    random.seed(42) # Ensures that the pool and search keywords are always the same
    keyword_pool = generate_large_keyword_pool(100)

    # Pick 10 keywords to search for
    client_keywords = random.sample(keyword_pool, 10)

    client_elements = [psi.hash_to_int(kwd) for kwd in client_keywords]
    return client_elements

def server_setup_SMALL_DATASET():
    return psi.server_setup()

def client_setup_SMALL_DATASET():
    # Enter test keywords
    client_keywords = ['apple', 'banana']

    client_elements = [psi.hash_to_int(kwd) for kwd in client_keywords]
    return client_elements


# Begin total timing
total_start_time = time.time()

# Here enter SMALL or LARGE to test either scenario
server_elements = server_setup_LARGE_DATASET()
client_elements = client_setup_LARGE_DATASET()

# Measure the time taken by client_transform()
start_time = time.time()
client_secret, client_transformed_elements = psi.client_transform(client_elements)
end_time = time.time()
client_transform_time = end_time - start_time

"""Client sends client_transformed_elements to server"""

# Measure the time taken by server_process()
start_time = time.time()
server_data = psi.server_process(server_elements, client_transformed_elements)
end_time = time.time()
server_process_time = end_time - start_time

"""Server sends server_transformed_elements and client_elements_server to client"""

# Measure the time taken by client_compute_intersection()
start_time = time.time()
counts = psi.client_compute_intersection(client_secret, server_data)
end_time = time.time()
client_compute_intersection_time = end_time - start_time

# End total timing
total_end_time = time.time()
total_time = total_end_time - total_start_time

print("\n")
for doc_id, count in counts:
    print(f"Document '{doc_id}' has {count} matching keyword(s).")

print("\n")
print(f"Time taken by client_transform(): {client_transform_time * 1000:.5f} milliseconds")
print(f"Time taken by server_process(): {server_process_time * 1000:.5f} milliseconds")
print(f"Time taken by client_compute_intersection(): {client_compute_intersection_time * 1000:.5f} milliseconds")
print(f"Total time taken: {total_time * 1000:.5f} milliseconds")
print("\n")