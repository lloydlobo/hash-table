// main.cpp

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <vector>

struct HashTable {
    HashTable(size_t size) : m_size(size), m_table(m_size, nullptr) {}

    ~HashTable() {
        for (Entry* entry : m_table) {
            while (entry != nullptr) {
                Entry* tmp = entry;
                entry = entry->next;
                delete tmp;
            }
        }
    }

    void insert(const char* key, const int val) {
        uint64_t index = djb2_hash(key);
        Entry* entry = new Entry{key, val};

        if (m_table[index] == nullptr) {
            m_table[index] = entry;
        } else {
            //
        }
    }

    int get(const char* key) {
        uint64_t index = djb2_hash(key);
        Entry* cur = m_table[index];
        while (cur != nullptr) {
            if (cur->key == key) {
                return cur->val;
            }
            cur = cur->next;
        }
        return -1;  // Key not found
    }

    // `djb2` Bernstein hash function updates the hash value using the formula
    // `(hash << 5) + hash + *key`. It iterates through each character,
    // left-shifting the current hash by 5 bits and adding the ASCII value.
    uint64_t djb2_hash(const char* key) {
        uint64_t hash = 5381;
        while (*key != '\0') {
            hash = (((hash << 5) + hash) + *key);  // hash * 33 + c;
            key++;
        }
        return (hash % m_size);
    }

   private:
    struct Entry {
        const char* key;
        int val;
        Entry* next;
    };

    const size_t m_size;
    std::vector<Entry*> m_table;
};

int main() {
    HashTable ht(100);  // Initialize the hash table

    // Insert some key-value pairs
    ht.insert("puppy", 5);
    ht.insert("kitty", 8);
    ht.insert("birdy", 12);

    // Retrieve values
    std::cout << "Count of puppy': " << ht.get("puppy") << std::endl;
    std::cout << "Count of kitty': " << ht.get("kitty") << std::endl;
    std::cout << "Count of wolfie': " << ht.get("")
              << std::endl;  // Should print -1

    return 0;
}
