# main.py

import hashlib
import sys
from enum import Enum
from itertools import cycle
from sys import exit

from faker import Faker


class HTHash:
    @staticmethod
    def jenkins_hash(key: str) -> int:
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
    def md5_hash(key: str) -> int:
        """MD5 (Message Digest Algorithm 5)"""
        md5 = hashlib.md5()
        md5.update(key.encode('utf-8'))
        return int((md5.hexdigest()), 16)

    @staticmethod
    def simple_hash(key: str) -> int:
        h_val = 0
        for c in key:  # Convert character to Unicode code point
            h_val += ord(c)
        return h_val

    @staticmethod
    def sha265_hash(key: str) -> int:
        """SHA-256 (Secure Hash Algorithm 256-bit)"""
        sha256 = hashlib.sha256()
        sha256.update(key.encode('utf-8'))
        return int((sha256.hexdigest()), 16)


class HashTable(HTHash):
    class FmtEntry(Enum):
        NODE, TREE = 'NODE', 'TREE'

    class Entry:
        def __init__(self, key: str, val: str) -> None:
            self.m_key: str = key
            self.m_val: str = val
            self.m_next: HashTable.Entry | None = None

    __m_cap: int
    __m_size: int
    __m_table: list[Entry | None]

    DEFAULT_CAPACITY: int = 16  # capacities = [16, 32, 64]
    LOAD_CAPACITY_THRESHOLD: float = 0.7

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        self.__m_cap = capacity
        self.__m_size = 0
        self.__m_table = ([None] * capacity)

    def clear(self) -> None:
        cur: HashTable.Entry | None
        # Detach current entry from the linked list
        # Move to the next entry in the linked list
        for i in range(self.__m_cap):
            cur = self.__m_table[i]
            while cur is not None:
                cur.m_next, cur = None, cur.m_next
                self.__m_size -= 1
            self.__m_table[i] = None  # Reset after clearing current linked list
        assert (self.__m_size == 0 and 'Should visit and clear all entry nodes')

    def get(self, key: str) -> Entry | None:
        cur: HashTable.Entry | None
        index = self.hash_key_to_index(key)
        cur = self.__m_table[index]
        while cur is not None:
            if cur.m_key == key:
                return cur
            cur = cur.m_next

    def hash_key_to_index(self, key):
        index = HTHash.jenkins_hash(key)
        return int(index % self.__m_cap)

    def insert(self, key: str, val: str) -> None:
        if self.__m_size >= (self.__m_cap * self.LOAD_CAPACITY_THRESHOLD):
            self.__resize()
        index = self.hash_key_to_index(key)
        if index > self.__m_cap:
            print("Index outside available range", file=sys.stderr)
            return
        entry: HashTable.Entry = self.Entry(key=key, val=val)
        if self.__m_table[index] is None:
            self.__m_table[index] = entry  # Insert new entry
            self.__m_size += 1
            return
        cur: HashTable.Entry | None = self.__m_table[index]
        while cur is not None:
            if cur.m_key == key:  # Update existing key's value
                self.__m_table[index].m_val = entry.m_val
                return
            elif cur.m_next is None:  # Avoid collision and add to linked list
                self.__m_table[index].m_next = entry
                self.__m_size += 1
                return
            cur = cur.m_next

    def capacity(self) -> int:
        return self.__m_cap

    def dbg_visit_all(self, fmt: FmtEntry = FmtEntry.TREE) -> None:
        print(fmt, self.__class__)
        for e in self.__m_table:
            HTPrinter.print_entry(e, fmt)

    def describe(self) -> None:
        HTPrinter.describe(self, self.__m_table)

    def is_empty(self) -> bool:
        cur: HashTable.Entry | None
        return all(cur is None for cur in self.__m_table)

    def size(self) -> int:
        return self.__m_size

    def __resize(self):
        cur: HashTable.Entry | None
        new_cap = self.__m_cap * 2
        new_table: list[HashTable.Entry | None] = [None] * new_cap
        for cur in self.__m_table:
            while cur is not None:  # Re-hash existing entries
                index = HTHash.jenkins_hash(cur.m_key)
                tmp, cur.m_next = cur.m_next, new_table[index]
                new_table[index], cur = cur, tmp
        self.__m_table = new_table
        self.__m_cap = new_cap


class HTPrinter:
    @staticmethod
    def print_entry(entry: HashTable.Entry | None,
                    fmt: HashTable.FmtEntry) -> None:
        if fmt == HashTable.FmtEntry.NODE:
            HTPrinter.print_node(entry)
        elif fmt == HashTable.FmtEntry.TREE:
            HTPrinter.print_tree(entry)

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
                HTPrinter.print_tree(entry.m_next, depth + 1)
                entry = entry.m_next

    @staticmethod
    def describe(ht: HashTable, entries: list[HashTable.Entry | None]) -> None:
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
        print('\t[\n' + '\t\t' + '\t\t'.join(
            buf) + '\t]') if not ht.is_empty() else print('\t[]')


def gen_fake_data(fake: Faker, count: int) -> list[HashTable.Entry]:
    keys, vals = fake.words(count), fake.sentences(count)
    return [HashTable.Entry(k, v) for k, v in zip(keys, vals)]


def main() -> int:
    ht_capacity = HashTable.DEFAULT_CAPACITY ** 2
    num_entries = 32

    fake = Faker()
    ht = HashTable(capacity=ht_capacity)

    fake_entries: list[HashTable.Entry] = gen_fake_data(fake, num_entries)
    ht_entries = cycle(fake_entries)
    for _ in range(num_entries):
        e = next(ht_entries)
        ht.insert(key=e.m_key, val=e.m_val)

    ht.insert('puppy', 'doggo')
    ht.insert('chick', 'chicken')

    ht.describe()
    ht.dbg_visit_all()
    ht.clear()

    return 0


if __name__ == '__main__':
    exit(main())
