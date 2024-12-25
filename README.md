# DATASHARE NETWORK Implementation

By: Teo Field-Marsham

This repository implements Private Set Intersection (PSI) and Multi-Set Private Set Intersection (MS-PSI) as described in the original paper *DatashareNetwork: A Decentralized Privacy-Preserving Search Engine for Investigative Journalists* by Kasra EdalatNejad (SPRING Lab, EPFL) et al from USENIX 2020.

## Private Set Intersection (PSI)

PSI allows a client and server to compute the intersection of their respective keyword sets (so 2 sets in total) without revealing any details of their sets. At a high level, the scheme is as follows:

### 1. Setup and Key Generation

- A large prime P and generator G are chosen (in this case, a 2048-bit prime from [RFC 7919](https://datatracker.ietf.org/doc/html/rfc7919)).  
- Each keyword is hashed (using BLAKE2b) to an integer under the group order $ \frac{P-1}{2} $ to obscure the original keywords.
- Each party (client and server) locally generates a random secret exponent mod $ \frac{P-1}{2} $.

### 2. Transformations

- The client exponentiates the hashed values with its secret ($ \text{hash}^s \mod P $
) and sends them to the server.
- The server exponentiates both its own hashed values and the clients exponentiated values with its own secret.

### 3. Intersection

- After receiving the servers further exponentiations, the client inversely exponentiates them to recover all valid collisions.
- The sets of tags are compared by hashing them again with some extra identifying information (e.g., document ID + exponentiated keyword).
- The client identifies which tags match and can conclude which keywords are in both sets and satisfy their query.

## Multi-Set Private Set Intersection (MS-PSI)

MS-PSI extends PSI by allowing multiset intersection (we have one server keyword set, but can have mutliple client keyword sets). In MS-PSI, each keyword can appear multiple times, and the intersection must respect these multiplicities (e.g. if the client has “apple” twice in their query, if the server has "apple" twice in their set, this will count as 2 matches).

The scheme flows similar to PSI:

### 1. Setup and Key Generation

- A large prime P and generator G are chosen (in this case, a 2048-bit prime from [RFC 7919](https://datatracker.ietf.org/doc/html/rfc7919).  
- Each keyword is hashed (using BLAKE2b) to an integer under the group order $ \frac{P-1}{2} $ to obscure the original keywords.
- Each party (client and server) locally generates a random secret exponent mod $ \frac{P-1}{2} $.

### 2. Transformations

- The client exponentiates the hashed values with its secret ($ \text{hash}^s \mod P $
) and sends them to the server.
- The server exponentiates both its own hashed values and the clients exponentiated values with its own secret.
- Additionaly to PSI, here a `Counter` is used to keep track of frequencies of elements.

### 3. Intersection

- After receiving the servers further exponentiations, the client inversely exponentiates them to recover all valid collisions.
- The client checks how many times a given hashed keyword appears in the server sets (while still not revealing the exact keywords).
- The result is a multiset intersection (you get not only which items intersect, but also how many times they match). 

## Results

The following test results have been obtained by running the PSI and MS-PSI algorithms 10 times with both the large and small datasets. They show the mean total time taken (in milliseconds) in each scenario. 

|        | Small dataset | Large dataset |   
|--------|---------------|---------------|
| PSI    |     317.59    |    10275.98   |
| MS-PSI |    1343.82    |    27795.98   |

These results clearly show that the extra functionalties of MS-PSI come at a cost of longer runtime under identical computational conditions and dataset sizes. MS-PSI's ability to handle multiplicities and return the exact ID's of matching keywords, compared to PSI which only returns the count(ignoring multiplicities) naturally increases the runtime.

Some potential optimizations that could narrow the performance gap include: parallelizing or batching the exponentiations, using a custom, specialized frequency counter or simply using a faster hashing or exponentiation library(a compiled C library instead of Python). 

In summary, more extensive testing (varying the number and size of documents, the exact distribution of keywords, testing on different hardware) could paint a more exact picture of the overall performance and performance gap of the two schemes. This data could then be used to optimize both schemes and make them as lightweight and efficient as possible, which are key requirements mentioned in the paper. Nevertheless, MS-PSI will always be more expensive than PSI, however its more extensive feature set, is simply required in certain situations.

## Differences to the original protocol

Firstly, in the example code by the authors of the original paper, values are chosen according to elliptic curve groups, whereas I create them according to prime-order groups with modular exponentiation for the discrete log (DLOG) problem. This was however according to the specifications of my assignment.

Another change I chose to make is to take the inital hashing step, where the keyword sets of both client and server are hashed, and do them in the very step. I did this because the paper describes a real-world scenario involving a central server that is constanlty receiving new keyword sets from journailists. I however, wanted to create a demo that can easily be run by any single user on a single device, but still keep this critical security feature. 

Lastly, in MS-PSI in the server_transform() function, in my code only the tag collection is returned and not N (N is the number of keyword sets the server holds). N is specified in the original protocol because it may be useful for performance optimizations or bounding loops in a theoretical implementation. Some implementations might also rely on N to preallocate memory or track progress, however in my Python implementation N is stored implicitly due to the nature of Python dictionaries and does not need to be returned explicitly. 

## Running the code

- **Python Version:** Ensure you have Python 3.8 or higher installed.
- **Dependencies:** Scripts use only built-in Python libraries, so no extra installations are necessary.
- **Installation:** Simply clone the [repository](https://github.com/TeoField-Marsham/Datashare_Network_implementation) and you are good to go! 

### PSI
To run the basic PSI example and interactively input your search keywords:

    python3 psi.py
    
Enter your desired keywords (eg. apple banana) and press Enter.

### Benchmarking PSI
To run performance tests for PSI (small or large keyword sets or different parameters), use:

    python3 benchmarking_psi.py
    
Functionality of the test needs to be adjusted within the code.

### MS-PSI
To run the MS-PSI example and interactively input your search keywords:

    python3 mspsi.py
    
Enter your desired keywords (eg. apple apple date banana) and press Enter.

### Benchmarking MS-PSI
To run performance tests for MSPSI (small or large keyword sets or different parameters), use:

    python3 benchmarking_mspsi.py
    
Functionality of the test needs to be adjusted within the code.
