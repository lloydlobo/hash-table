# main.py

import hashlib
from enum import Enum
from sys import exit
from typing import List


class HashTable:
    # data structures:

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
        """
        @usage:
            `ht = HashTable()`
            `ht = HashTable(HashTable.DEFAULT_CAPACITY)`

        :type capacity: int
        :rtype: None
        :param capacity: Capacity of hash table.
            (Default: 16 or `HashTable.DEFAULT_CAPACITY`)
        """
        self.__m_cap = capacity
        self.__m_size = 0
        self.__m_table = ([None] * capacity)

    def clear(self) -> None:
        cur: HashTable.Entry | None
        tmp: HashTable.Entry | None

        for i in range(self.__m_cap):
            cur = self.__m_table[i]
            while cur is not None:
                tmp = cur.m_next
                cur.m_next = None  # Detach current entry from the linked list
                cur = tmp  # Move to the next entry in the linked list
                self.__m_size -= 1  # Decrement the size for each entry
            # Set the slot to None after clearing current linked list
            self.__m_table[i] = None
        assert (self.__m_size == 0 and 'Should visit and clear all entry nodes')

    def get(self, key: str) -> Entry | None:
        cur: HashTable.Entry | None

        index = self.__jenkins_hash(key)
        cur = self.__m_table[index]

        while cur is not None:
            if cur.m_key == key:
                return cur
            cur = cur.m_next

    def insert(self, key: str, val: str) -> None:
        entry: HashTable.Entry
        cur: HashTable.Entry | None

        if self.__m_size >= self.__m_cap:
            return

        index = self.__jenkins_hash(key)
        entry = self.Entry(key=key, val=val)
        if self.__m_table[index] is None:
            self.__m_table[index] = entry  # Insert new entry
            self.__m_size += 1
            return

        cur = self.__m_table[index]
        while cur is not None:
            if cur.m_key == key:  # Update existing key's value
                self.__m_table[index].m_val = entry.m_val
                break
            elif cur.m_next is None:  # Avoid collision and add to linked list
                self.__m_table[index].m_next = entry
                self.__m_size += 1
                break
            cur = cur.m_next

    def capacity(self) -> int:
        return self.__m_cap

    def describe(self) -> None:
        Printer.print_table_info(self, self.__m_table)

    def is_empty(self) -> bool:
        cur: HashTable.Entry | None
        # for cur in self.__m_table: if cur is not None: return False
        # return True
        return all(cur is None for cur in self.__m_table)

    def size(self) -> int:
        return self.__m_size

    def dbg_visit_all(self, fmt: FmtEntry = FmtEntry.TREE) -> None:
        print(fmt, self.__class__)
        for e in self.__m_table:
            Printer.print_entry(e, fmt)

    # private:

    def __jenkins_hash(self, key: str) -> int:
        """A non-cryptographic hash function designed for good distribution"""
        h_val: int = 0
        for c in key:
            h_val += ord(c)
            h_val += (h_val << 10)
            h_val ^= (h_val >> 6)
        h_val += (h_val << 3)
        h_val ^= (h_val >> 11)
        h_val += (h_val << 15)
        return h_val % self.__m_cap

    def __simple_hash(self, key: str) -> int:
        h_val = 0
        for c in key:  # Convert character to Unicode code point
            h_val += ord(c)
        return h_val % self.__m_cap

    def __sha265_hash(self, key: str) -> int:
        """SHA-256 (Secure Hash Algorithm 256-bit)"""
        sha256 = hashlib.sha256()
        sha256.update(key.encode('utf-8'))
        return int((sha256.hexdigest()), 16) % self.__m_cap

    def __md5_hash(self, key: str) -> int:
        """MD5 (Message Digest Algorithm 5)"""
        md5 = hashlib.md5()
        md5.update(key.encode('utf-8'))
        return int((md5.hexdigest()), 16) % self.__m_cap


class Printer:
    @staticmethod
    def print_entry(entry: HashTable.Entry | None,
                    fmt: HashTable.FmtEntry) -> None:
        if fmt == HashTable.FmtEntry.NODE:
            Printer.print_node(entry)
        elif fmt == HashTable.FmtEntry.TREE:
            Printer.print_tree(entry)

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
                Printer.print_tree(entry.m_next, depth + 1)
                entry = entry.m_next

    @staticmethod
    def print_table_info(table: HashTable,
                         entries: List[HashTable.Entry | None]) -> None:
        buf: List[str] = list()
        for i, entry in enumerate(entries):
            linked_list_depth = 0
            cur = entry
            while cur is not None:
                buf.append(
                    f'{i}->{linked_list_depth}:\t{cur.m_key}: {cur.m_val}\n')
                linked_list_depth += 1
                cur = cur.m_next

        print(table.__class__)
        print(
            f'\tsize:{table.size()}, ' f'capacity:{table.capacity()}, '
            f'is_empty:{table.is_empty()}')
        if not table.is_empty():
            print('\t[')
            print('\t\t' + '\t\t'.join(buf), end='')
            print('\t]')
        else:
            print('\t[]')


def main() -> int:
    print('Hash Table in Python\n')

    ht = HashTable(capacity=22)
    ht.describe()
    keys = ['puppy', 'kitten', 'cub']
    vals = ['doggie', 'cat', 'lion']
    for k, v in zip(keys, vals):
        ht.insert(key=k, val=v)
    ht.describe()
    for k, v in zip(keys, vals):
        entry = ht.get(k)
        assert (entry.m_key == k and entry.m_val == v)
    ht.dbg_visit_all()
    ht.clear()

    ht.insert('puppy', 'doggo')
    ht.insert('chick', 'chicken')
    ht.dbg_visit_all()

    return 0


if __name__ == '__main__':
    exit(main())
