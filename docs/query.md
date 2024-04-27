## Bloom Filters in RocksDB

**Definition:** A probabilistic data structure that tests whether an element is a member of a set.

**Purpose:** Primarily used to optimize read operations by quickly checking if a key is possibly in a dataset.

**Operation:**
When RocksDB looks up a key, it first checks the Bloom filter.
If the filter indicates the key is not present, RocksDB avoids a disk read.
If the filter indicates the key might be present (false positives are possible), RocksDB proceeds to check on-disk data.

**Advantages:** Significantly reduces disk I/O for read operations, thus improving performance.

**Configurability:** Can be tuned for different sizes and false positive rates depending on the application needs.

## Merge Operations in RocksDB

**Definition:** A type of write operation that combines new data with existing data for a key.

**Functionality:**
Allows for the coalescing of multiple updates into a single value without reading the data first.
Useful for incrementing counters, appending to a list, or combining multiple datasets.
Usage:
A merge operator must be defined to specify how to combine the existing value with the new data.
During a read, compaction, or flush, the merge operator is applied to resolve the final value.
Benefits: Reduces the need for read-modify-write cycles, which can improve write throughput and reduce latency.
Querying Data in RocksDB

**Key-Value Operations**

_Get:_ Retrieves the value for a specific key.
_Put:_ Sets the value for a key.
_Delete:_ Removes a key-value pair.

**Iterators:**

Allow sequential access to key-value pairs within the database.
Can be used to efficiently scan through a range of keys.

**Prefix Scans:**

Optimized scans for keys that share a common prefix.
Can leverage prefix-specific Bloom filters for improved efficiency.

**Snapshot Reads:**

Provide a consistent view of the database at a point in time.
Useful for read-heavy workloads requiring isolation between reads and writes.

**Range Queries:**

Enable querying of keys within a specific key range.
Useful for batch operations or when working with sorted data.
Advanced Query Features

**Column Families:**

Allows separation of data into distinct namespaces within the same database instance.
Each column family can have its configuration, compaction strategy, and cache.

**Compaction Filters:**

Customizable logic that runs during compactions to remove or alter key-value pairs.
Can be used to implement TTL (time-to-live) or remove logically deleted items.

**Subcompactions:**

Improves performance by parallelizing compactions within a column family.
Useful for write-heavy workloads or reducing latency during compactions.