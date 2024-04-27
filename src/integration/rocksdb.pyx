# rocksdb_wrapper.pyx
import orjson
from libcpp cimport bool
from libcpp.string cimport string


cdef extern from "rocksdb/db.h" namespace "rocksdb":
    cdef cppclass DB:
        @staticmethod
        Status Open(const Options&, const string&, DB**)
        void Put(const WriteOptions&, const string&, const string&)
        Status Get(const ReadOptions&, const string&, string*)
        Status Delete(const WriteOptions&, const string&)
        Status Merge(const WriteOptions&, const string&, const string&)
        Iterator* NewIterator(const ReadOptions&)
        void Close()

    cdef cppclass Options:
        Options()
        bool create_if_missing

    cdef cppclass WriteOptions:
        WriteOptions()

    cdef cppclass ReadOptions:
        ReadOptions()

    cdef cppclass Status:
        bool ok()
        string ToString()

    cdef cppclass Iterator:
        void SeekToFirst()
        void Next()
        bool Valid()
        Slice key()
        Slice value()
        void Close()

    cdef cppclass Slice:
        const char* data()
        size_t size()
    
    cdef cppclass Comparator:
        Comparator()
        int Compare(const string&, const string&)
        const char* Name()

    cdef cppclass FilterPolicy:
        FilterPolicy()
        const char* Name()
        char* CreateFilter(const string*, int, size_t*)
        bool KeyMayMatch(const string&, const string&, size_t)

    cdef cppclass Cache:
        Cache()
        const char* Name()
        void* Insert(const string&, void*, size_t, void (*)(const string&, void*))
        void* Lookup(const string&, size_t, void (*)(const string&, void*))
        void Release(void*, size_t)
        void Erase(const string&)
        size_t TotalCharge()
        void* Value(void*)
        void SetCapacity(size_t)
        size_t GetCapacity()
        void* GetStats()
        void Dispose()
        void SetStrictCapacityLimit(bool)
        void ApplyToAllCacheEntries(void (*)(const string&, void*), bool)

    cdef cppclass Snapshot:
        Snapshot()
        void Release()

    cdef cppclass ColumnFamilyHandle:
        ColumnFamilyHandle()
        void SetName(const string&)
        string GetName()
        void Destroy()

cdef class RocksDBWrapper:
    cdef DB* db
    cdef Options options
    cdef WriteOptions write_options
    cdef ReadOptions read_options
    cdef Status status
    cdef Iterator* it
    cdef string key
    cdef string value
    cdef int count
    cdef string db_path
    cdef string key_prefix

    def __cinit__(self, str db_path):
        if not db_path:
            raise ValueError("db_path must be provided")
        self.options = Options()
        self.options.create_if_missing = True
        self.write_options = WriteOptions()
        self.read_options = ReadOptions()
        cdef Status status
        status = DB.Open(self.options, db_path.encode(), &self.db)
        if not status.ok():
            raise Exception(status.ToString())

    def __dealloc__(self):
        if self.db:
            self.db.Close()

    def put(self, str key, bytes value):
        self.db.Put(self.write_options, key.encode(), value)

    def get(self, str key):
        cdef Status status
        cdef string value
        status = self.db.Get(self.read_options, key.encode(), &value)
        if not status.ok():
            return None
        return value

    def delete(self, str key):
        self.db.Delete(self.write_options, key.encode())

    def __iter__(self):
        cdef Iterator* it = self.db.NewIterator(self.read_options)
        try:
            it.SeekToFirst()
            while it.Valid():
                key = (<bytes>it.key().data())[:it.key().size()]
                value = (<bytes>it.value().data())[:it.value().size()]
                yield key, value
                it.Next()
        finally:
            del it

cdef class Collection:
    cdef RocksDBWrapper db

    def __cinit__(self, str db_path):
        self.db = RocksDBWrapper(db_path)

    def exists(self, str key)->bool:
        return self.db.get(key) is not None

    def get(self, str key):
        cdef bytes value = self.db.get(key)
        if value is None:
            return None
        return orjson.loads(value)

    def create(self, str key, object value):
        if self.exists(key):
            raise ValueError(f"Object with id {key} already exists")
        self.db.put(key, orjson.dumps(value, option=orjson.OPT_SERIALIZE_NUMPY))
        
    def update(self, str key, object value):
        if not self.exists(key):
            raise ValueError(f"Object with id {key} not found")
        self.db.put(key, orjson.dumps(value, option=orjson.OPT_SERIALIZE_NUMPY))

    def delete(self, str key):
        if not self.exists(key):
            raise ValueError(f"Object with id {key} not found")
        self.db.delete(key)

    def find_one(self, str key):
        if self.exists(key):
            return self.get(key)
        return {key: None}

    def find_all(self):
        cdef list results = []
        cdef Iterator* it = self.db.db.NewIterator(self.db.read_options)
        try:
            it.SeekToFirst()
            while it.Valid():
                value = (<bytes>it.value().data())[:it.value().size()]
                results.append(orjson.loads(value))
                it.Next()
        finally:
            del it
        return results

    def find_many(self, object kwargs):
        cdef list results = []
        cdef Iterator* it = self.db.db.NewIterator(self.db.read_options)
        try:
            it.SeekToFirst()
            while it.Valid():
                key = (<bytes>it.key().data())[:it.key().size()]
                value = (<bytes>it.value().data())[:it.value().size()]
                value_dict = orjson.loads(value)  # Parse bytes to dict
                if all(value_dict.get(k) == v for k, v in kwargs.items()):
                    results.append(value_dict)
                it.Next()
        finally:
            del it
        return results

    def count(self):
        cdef int count = 0
        cdef Iterator* it = self.db.db.NewIterator(self.db.read_options)
        try:
            it.SeekToFirst()
            while it.Valid():
                count += 1
                it.Next()
        finally:
            del it
        return count

    def find_first(self):
        cdef Iterator* it = self.db.db.NewIterator(self.db.read_options)
        try:
            it.SeekToFirst()
            if it.Valid():
                value = (<bytes>it.value().data())[:it.value().size()]
                return orjson.loads(value)
        finally:
            del it
        return None

    def find_last(self):
        cdef Iterator* it = self.db.db.NewIterator(self.db.read_options)
        try:
            it.SeekToFirst()
            while it.Valid():
                value = (<bytes>it.value().data())[:it.value().size()]
                it.Next()
                return orjson.loads(value)
        finally:
            del it
        return None