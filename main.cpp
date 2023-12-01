// main.cpp

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <optional>
#include <vector>

struct HashTable {
    explicit HashTable(size_t size) : m_size(size), m_table(m_size) {}

    ~HashTable() = default;  // The default destructor

    // Insert via 'linear probing' instead of 'chaining' collision strategy.
    void insert(const char *key, const int val) {
        uint64_t index = fnv1a_hash(key);
        auto entry = std::make_shared<Entry>(key, val);
        index = linear_probe(key, index);
        if (m_table[index] == nullptr)  // Key not found, insert new entry
            m_table[index] = entry;     // Insert success
        else
            m_table[index]->val = val;  // Update success
    }

    std::optional<int> get(const char *key) {
        uint64_t index = fnv1a_hash(key);
        auto cur_entry = m_table[index].get();
        while (cur_entry != nullptr) {
            if (std::strcmp(cur_entry->key, key) == 0) return cur_entry->val;
            cur_entry = cur_entry->next.get();
        }
        return std::nullopt;  // Key not found
    }

   private:
    // FNV-1a hash algorithm used for better distribution than `djb2`.
    uint64_t fnv1a_hash(const char *key) {
        uint64_t hash = 14695981039346656037ull;
        while (*key != '\0') {
            hash ^= static_cast<uint64_t>(*key);
            hash *= 1099511628211ul;
            key += 1;
        }
        return (hash % m_size);
    }

    // `djb2` Bernstein hash function updates the hash value using the
    // formula `(hash << 5) + hash + *key`. It iterates through each character,
    // left-shifting the current hash by 5 bits and adding the ASCII value.
    uint64_t djb2_hash(const char *key) {
        uint64_t hash = 5381;
        while (*key != '\0') {
            hash = (((hash << 5) + hash) + *key++);  // hash * 33 + c;
        }
        return (hash % m_size);
    }

    uint64_t linear_probe(const char *key, uint64_t index) {
        auto step = 1;
        while (m_table[index] != nullptr) {
            if (std::strcmp(m_table[index]->key, key) == 0)
                return index;                   // Key already exists
            index = ((index + step) % m_size);  // Move to the next slot
        }
        return index;
    }

    struct Entry {
        const char *key;
        int val;
        std::shared_ptr<Entry> next;

        explicit Entry(const char *k, int v) : key(k), val(v), next(nullptr) {}
    };

    // members:

    const size_t m_size;
    std::vector<std::shared_ptr<Entry>> m_table;
};

void print_result(const char *key, std::optional<int> result) {
    if (result.has_value())
        std::cout << "Count of " << key << ": " << result.value() << '\n';
    else
        std::cout << "Key '" << key << "' not found" << '\n';
}

int main() {
    constexpr size_t table_size = 100;
    std::vector<std::pair<const char *, int>> keyval_pairs;
    HashTable ht(table_size);  // Initialize the hash table
    keyval_pairs = {{"puppy", 5}, {"kitty", 8}, {"horsie", 12}};

    for (const auto &kv : keyval_pairs)  // Insert some key-value pairs
        ht.insert(kv.first, kv.second);
    ht.insert("puppy", 7);  // Update a key

    for (const auto &kv : keyval_pairs)  // Retrieve values
        print_result(kv.first, ht.get(kv.first));
    print_result("wolfie", ht.get("wolfie"));  // Key 'wolfie' not found

    return 0;
}
