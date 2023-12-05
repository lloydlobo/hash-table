# main.py

import hashlib
from copy import copy
from enum import Enum
from functools import lru_cache
from itertools import cycle
from sys import exit

from faker import Faker


class HTHashFn:
    class FnType(Enum):
        fnv1a = 'fnv1a'
        jenkins = 'jenkins'
        md5 = 'md5'
        sha256 = 'sha256'
        simple = 'simple'

    @classmethod
    def hash(cls, key: str, hash_fn: FnType = FnType.jenkins):
        """
        @usage:
            hash_value = HashTableHashFn.hash("example_key",
                                              hash_fn=HTHashFn.FnType.md5)
        """
        match hash_fn:
            case cls.FnType.fnv1a:
                return cls.__fnv1a_hash(key)
            case cls.FnType.jenkins:
                return cls.__jenkins_hash(key)
            case cls.FnType.md5:
                return cls.__md5_hash(key)
            case cls.FnType.simple:
                return cls.__simple_hash(key)
            case cls.FnType.sha256:
                return cls.__sha256_hash(key)
            case _:
                raise ValueError(
                    f'Invalid hash function: {repr(hash_fn)}\n'
                    f'[INFO]\tAvailable hash functions:\n'
                    f'\t\t{'\n\t\t'.join(list(cls.FnType.__members__.keys()))}'
                )

    @staticmethod
    @lru_cache(maxsize=None)
    def __fnv1a_hash(key: str) -> int:
        """FNV-1a hash algorithm used for better distribution than `djb2`"""
        h_val = 14695981039346656037
        for c in key:
            h_val ^= ord(c)
            h_val *= 1099511628211
        return int(h_val)

    @staticmethod
    @lru_cache(maxsize=None)
    def __jenkins_hash(key: str) -> int:
        """A non-cryptographic hash function designed for good distribution"""
        h_val: int = 0
        for c in key:
            h_val += ord(c)
            h_val += (h_val << 10)
            h_val ^= (h_val >> 6)
        h_val += (h_val << 3)
        h_val ^= (h_val >> 11)
        h_val += (h_val << 15)
        return int(h_val)

    @staticmethod
    @lru_cache(maxsize=None)
    def __md5_hash(key: str) -> int:
        """MD5 (Message Digest Algorithm 5)"""
        md5 = hashlib.md5()
        md5.update(key.encode('utf-8'))
        return int((md5.hexdigest()), 16)

    @staticmethod
    @lru_cache(maxsize=None)
    def __sha256_hash(key: str) -> int:
        """SHA-256 (Secure Hash Algorithm 256-bit)"""
        sha256 = hashlib.sha256()
        sha256.update(key.encode('utf-8'))
        return int((sha256.hexdigest()), 16)

    @staticmethod
    @lru_cache(maxsize=None)
    def __simple_hash(key: str) -> int:
        h_val = 0
        for c in key:  # Convert character to Unicode code point
            h_val += ord(c)
        return h_val


class HashTable:
    DEFAULT_CAPACITY: int = 16  # capacities = [16, 32, 64]
    LOAD_CAPACITY_THRESHOLD: float = 0.7

    class FmtEntry(Enum):
        NODE, TREE = 'NODE', 'TREE'

    class Entry:
        def __init__(self, key: str, val: str) -> None:
            self.m_key: str = key
            self.m_val: str = val
            self.m_next: HashTable.Entry | None = None

    __m_cap: int
    __m_hash_fn: HTHashFn.FnType
    __m_size: int
    __m_table: list[Entry | None]

    def __init__(self, capacity: int = DEFAULT_CAPACITY,
                 hash_fn: HTHashFn.FnType = HTHashFn.FnType.jenkins) -> None:
        self.__m_cap = capacity
        self.__m_hash_fn = hash_fn
        self.__m_size = 0
        self.__m_table = ([None] * capacity)
        self.m_entries_read = 0  # Amount of entries visited (insert or update in total in this instance life from start to finish)
        self.m_entries_updated = 0  # Amount of entries visited (insert or update in total in this instance life from start to finish)
        self.key_freq_dict = dict()
        self.resize_additive_multiplier = 1

    def clear(self) -> None:
        cur: HashTable.Entry | None
        for i in range(self.__m_cap):
            cur = self.__m_table[i]
            while cur is not None:
                # Detach current entry from the linked list
                # Move to the next entry in the linked list
                cur.m_next, cur = None, cur.m_next
                self.__m_size -= 1
            self.__m_table[i] = None  # Reset after clearing current linked list
        # NOTE: this could fail.
        assert (self.__m_size == 0 and 'Should visit and clear all entry nodes')

    def get(self, key: str) -> Entry | None:
        cur: HashTable.Entry | None
        index = self.hash_key_to_index(key)
        cur = self.__m_table[index]
        while cur is not None:
            if cur.m_key == key:
                return cur
            cur = cur.m_next

    def get_bucket_node(self, index: int) -> Entry | None:
        return copy(self.__m_table[index])

    def get_bucket_as_tuples(self, index: int) -> list[tuple[str, str]] | None:
        cur = copy(self.__m_table[index])
        if cur is None:
            return None
        bucket = list()
        while cur is not None:
            bucket.append((cur.m_key, cur.m_val))
            cur = cur.m_next
        return bucket

    def bucket_to_reversed(self, index) -> Entry | None:
        print('reversing....')
        head = copy(self.__m_table[index])
        if head is None:
            return None
        cur = copy(head)
        prev: HashTable.Entry | None = None

        while cur is not None:
            nxt, cur.m_next = cur.m_next, prev
            prev, cur = cur, nxt

        print('reversing done')

        return copy(prev)

    def hash_key_to_index(self, key) -> int:
        return int(
            HTHashFn.hash(key=key, hash_fn=self.__m_hash_fn) % self.__m_cap)

    def insert(self, key: str, val: str) -> None:
        self.m_entries_read += 1
        # Check if there's an existing entry with the same key
        existing_entry = self.get(key)
        if existing_entry:  # Update the existing entry with the new value
            existing_entry.m_val = val
            self.m_entries_updated += 1
            self.__record_dup_key_freq(key)
        else:
            index = self.hash_key_to_index(key)
            prev, cur = None, self.__m_table[index]
            while cur:
                if cur.m_key == key:
                    if prev:  # If duplicate key is found, remove the existing entry
                        prev.m_next = cur.m_next
                    else:  # If duplicate is first entry, update head of the list
                        self.__m_table[index] = cur.m_next
                    self.__m_size -= 1
                    break
                prev, cur = cur, cur.m_next
            # Insert the new entry at the beginning of the linked list
            entry = self.Entry(key, val)
            entry.m_next = self.__m_table[index]
            self.__m_table[index] = entry
            self.__m_size += 1

        if (self.__m_size / self.__m_cap) > self.LOAD_CAPACITY_THRESHOLD:
            self.__resize()  # Resize if needed

    def __record_dup_key_freq(self, key):
        if self.key_freq_dict.get(key) is None:  # Just for fun
            self.key_freq_dict[key] = 1
        else:
            self.key_freq_dict[key] += 1

    # Inside the HashTable class
    def pretty_print(self) -> None:
        print("HashTable Pretty Print:")
        print(f"\tSize: {self.size()}, Capacity: {self.capacity()}, "
              f"Is Empty: {self.is_empty()}")
        for i, entry in enumerate(self.__m_table):
            cur = entry
            # if cur is not None:
            #     print(f"\tBucket {i}:")
            print(f"\tBucket {i}:")
            while cur is not None:
                print(f"\t\t\t\t{cur.m_key}: {cur.m_val}")
                cur = cur.m_next

    def capacity(self) -> int:
        return self.__m_cap

    def dbg_visit_all(self, fmt: FmtEntry = FmtEntry.TREE) -> None:
        print(fmt, self.__class__)
        for e in self.__m_table:
            HashTablePrinter.print_entry(e, fmt)

    def describe(self) -> None:
        HashTablePrinter.describe_hashtable(self, self.__m_table)

    def is_empty(self) -> bool:
        cur: HashTable.Entry | None
        return all(cur is None for cur in self.__m_table)

    @staticmethod
    def print_bucket(bucket: Entry | None) -> None:
        if bucket is None:
            return
        cur = copy(bucket)
        while cur is not None:
            print(f'{repr(cur.m_key)}:', repr(cur.m_val))
            cur = cur.m_next

    def size(self) -> int:
        return self.__m_size

    def __resize(self):
        cur: HashTable.Entry | None
        new_cap = int(
            self.__m_cap + int(self.__m_cap * self.resize_additive_multiplier))
        new_table: list[HashTable.Entry | None] = [None] * new_cap
        for cur in self.__m_table:
            while cur is not None:  # Re-hash existing entries
                index = self.hash_key_to_index(cur.m_key)
                tmp, cur.m_next = cur.m_next, new_table[index]
                new_table[index], cur = cur, tmp
        self.__m_table = new_table
        self.__m_cap = new_cap


class HashTablePrinter:
    @staticmethod
    def print_entry(entry: HashTable.Entry | None,
                    fmt: HashTable.FmtEntry) -> None:
        if fmt == HashTable.FmtEntry.NODE:
            HashTablePrinter.print_node(entry)
        elif fmt == HashTable.FmtEntry.TREE:
            HashTablePrinter.print_tree(entry)

    @staticmethod
    def print_node(entry: HashTable.Entry | None) -> None:
        if entry is not None:
            print(f'({repr(entry.m_key)}: {repr(entry.m_val)}) -> '
                  f'{None if entry.m_next is None else ""}')

    @staticmethod
    def print_tree(entry: HashTable.Entry | None, depth: int = 0) -> None:
        if entry is not None:
            indent = '│   ' * depth + '└─ '
            print(f'{indent}{repr(entry.m_key)}: {repr(entry.m_val)}')
            while entry.m_next is not None:
                HashTablePrinter.print_tree(entry.m_next, depth + 1)
                entry = entry.m_next
        else:
            return

    @staticmethod
    def describe_hashtable(ht: HashTable,
                           entries: list[HashTable.Entry | None]) -> None:
        buf: list[str] = list()
        for i, entry in enumerate(entries):
            cur = entry
            depth = 0
            while cur is not None:
                buf.append(f'{i}->{depth}:\t{cur.m_key}: {cur.m_val}\n')
                cur = cur.m_next
                depth += 1
        print(ht.__class__)
        print(f'\tsize:{ht.size()}, capacity:{ht.capacity()}, '
              f'is_empty:{ht.is_empty()}')
        print('num_entries_read:', ht.m_entries_read, 'num_entries_updated:',
              ht.m_entries_updated)
        print('\t[\n' + '\t\t' + '\t\t'.join(
            buf) + '\t]') if not ht.is_empty() else print('\t[]')


def gen_fake_data(fake: Faker, count: int) -> list[HashTable.Entry]:
    keys, vals = fake.words(count), fake.sentences(count)
    return [HashTable.Entry(key=k, val=v) for k, v in zip(keys, vals)]


def main() -> int:
    ht_capacity = (HashTable.DEFAULT_CAPACITY ** 1)
    num_entries = (2 * (10 ** 4))

    fake = Faker()
    ht = HashTable(capacity=ht_capacity, hash_fn=HTHashFn.FnType.sha256)

    fake_entries: list[HashTable.Entry] = gen_fake_data(fake, num_entries)
    ht_entries: cycle[HashTable.Entry] = cycle(fake_entries)

    for _ in range(num_entries):
        e = next(ht_entries)
        ht.insert(key=e.m_key, val=e.m_val)
    assert ht.m_entries_read == num_entries

    ht.describe()
    # ht.dbg_visit_all()

    ht.pretty_print()

    print(len(ht.key_freq_dict), ht.key_freq_dict)

    index = ht.hash_key_to_index('always')
    ht.print_bucket(ht.get_bucket_node(index))
    ht.print_bucket(ht.bucket_to_reversed(index))
    # ht.clear()

    return 0


if __name__ == '__main__':
    exit(main())

"""
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int, hash_fn):
        self.capacity = capacity
        self.hash_fn = hash_fn
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            # Move the accessed key to the end to mark it as most recently used
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            # If key is not in the cache, calculate the hash and store it
            hash_value = self.hash_fn(key)
            self.cache[key] = hash_value
            # Check if the cache exceeds its capacity, and remove the least recently used entry
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)  # last=False means FIFO order
            return hash_value

    def clear(self):
        self.cache.clear()

# Example usage with your HTHashFn class
hash_fn = HTHashFn.hash
lru_cache = LRUCache(capacity=10, hash_fn=hash_fn)

key1 = "example_key1"
key2 = "example_key2"

# First access for key1, calculate hash and store in cache
hash_value1 = lru_cache.get(key1)
print(f"Hash for {key1}: {hash_value1}")

# Access key2, calculate hash and store in cache
hash_value2 = lru_cache.get(key2)
print(f"Hash for {key2}: {hash_value2}")

# Access key1 again, retrieve from cache without recalculating the hash
cached_hash_value1 = lru_cache.get(key1)
print(f"Cached hash for {key1}: {cached_hash_value1}")

# Clear the cache
lru_cache.clear()

"""
