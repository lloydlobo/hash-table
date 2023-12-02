# main.py

import hashlib
from sys import exit


class HashTable:
    def __init__(self, capacity: int) -> None:
        self.__m_table: list[HashTable.Entry | None] = [None] * capacity
        self.__m_cap: int = capacity
        self.__m_size: int = 0

    class Entry:
        def __init__(self, key: str, val: str) -> None:
            self.m_key: str = key
            self.m_val: str = val
            self.m_next: HashTable.Entry | None = None

    def clear(self) -> None:
        for i in range(self.__m_cap):
            cur: HashTable.Entry | None = self.__m_table[i]
            while cur is not None:
                tmp = cur.m_next
                cur.m_next = None  # Detatch current entry from the linked list
                cur = tmp  # Move to the next entry in the linked list
                self.__m_size -= 1  # Decrement the size for each entry
            # Set the slot to None after clearing current linked list
            self.__m_table[i] = None
        assert (self.__m_size == 0 and 'Should visit and clear all entry nodes')

    def get(self, key: str) -> Entry | None:
        index: int = self.__jenkins_hash(key)
        cur: HashTable.Entry | None = self.__m_table[index]

        while cur is not None:
            if cur.m_key == key:
                return cur
            cur = cur.m_next

    def insert(self, key: str, val: str) -> None:
        if self.__m_size >= self.__m_cap:
            return

        index: int = self.__jenkins_hash(key)
        entry: HashTable.Entry = self.Entry(key=key, val=val)

        if self.__m_table[index] is None:
            self.__m_table[index] = entry  # Insert new entry
            self.__m_size += 1
            return

        cur: HashTable.Entry | None = self.__m_table[index]

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
        for i in range(self.__m_cap):
            linked_list_depth = 0
            cur: HashTable.Entry | None = self.__m_table[i]

            while cur is not None:
                print(i, linked_list_depth, cur.m_key, cur.m_val)
                linked_list_depth += 1
                cur = cur.m_next

        print(f'size: {self.size()} ' f'capacity: {self.capacity()} '
              f'is_empty: {self.is_empty()}\n')

    def is_empty(self) -> bool:
        return self.__m_size == 0

    def size(self) -> int:
        return self.__m_size

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


def main() -> int:
    print('Hash Table in Python\n')

    ht_capacity = 22
    ht = HashTable(ht_capacity)
    ht.describe()

    keys = ['puppy', 'kitten', 'cub']
    vals = ['doggie', 'cat', 'lion']

    for k, v in zip(keys, vals):
        ht.insert(key=k, val=v)

    # for k, _ in zip(keys, vals):
    #     entry = ht.get(k)
    #     print(entry.m_key, entry.m_val)
    ht.describe()

    ht.insert('puppy', 'doggo')
    ht.describe()

    ht.insert('chick', 'chicken')
    ht.describe()

    ht.clear()
    ht.describe()

    ht.insert('chick', 'chicken')
    ht.describe()

    return 0


if __name__ == '__main__':
    exit(main())
