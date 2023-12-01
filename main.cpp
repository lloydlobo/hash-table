// main.cpp

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <vector>

struct HashTable {
    HashTable(size_t size) : m_size(size), m_table(m_size) {}

    ~HashTable() {
        for (auto &entry : m_table) {
            while (entry != nullptr) {
                auto tmp = std::move(entry);
                entry = std::move(tmp->next);
            }
        }
    }

    void insert(const char *key, const int val) {
        uint64_t index = djb2_hash(key);
        auto entry = std::make_unique<Entry>(key, val);

        // Key not found, insert new entry
        if (m_table[index] == nullptr) {
            m_table[index] = std::move(entry);
            return;
        }

        auto cur = m_table[index].get();

        while (cur != nullptr) {
            if (std::strcmp(cur->key, key) == 0) {
                cur->val = val;
                return;
            }
            if (cur->next == nullptr) break;

            cur = cur->next.get();
        }
    }

    int get(const char *key) {
        auto cur_entry = m_table[djb2_hash(key)].get();

        while (cur_entry != nullptr) {
            if (std::strcmp(cur_entry->key, key) == 0) return cur_entry->val;
            cur_entry = cur_entry->next.get();
        }
        return -1;  // Key not found
    }

   private:
    // `djb2` Bernstein hash function updates the hash value using the formula
    // `(hash << 5) + hash + *key`. It iterates through each character,
    // left-shifting the current hash by 5 bits and adding the ASCII value.
    uint64_t djb2_hash(const char *key) {
        uint64_t hash = 5381;
        while (*key != '\0') {
            hash = (((hash << 5) + hash) + *key);  // hash * 33 + c;
            key++;
        }
        return (hash % m_size);
    }

    struct Entry {
        const char *key;
        int val;
        std::unique_ptr<Entry> next;

        Entry(const char *k, int v) : key(k), val(v), next(nullptr) {}
    };
    const size_t m_size;
    std::vector<std::unique_ptr<Entry>> m_table;
};

int main() {
    const char *const keys[3] = {"puppy", "kitty", "horsie"};
    const int values[3] = {5, 8, 12};

    // Initialize the hash table
    HashTable ht(100);

    // Insert some key-value pairs
    for (size_t i = 0; i < 3; i += 1) ht.insert(keys[i], values[i]);

    ht.insert("puppy", 7);  // Update a key

    // Retrieve values
    std::cout << "Count of puppy': " << ht.get("puppy") << std::endl;
    std::cout << "Count of kitty': " << ht.get("kitty") << std::endl;
    std::cout << "Count of wolfie': " << ht.get("wolfie")
              << std::endl;  // Should print -1

    return 0;
}
