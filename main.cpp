// main.cpp

#include <cstring>
#include <iostream>
#include <memory>
#include <optional>
#include <vector>

struct HashTable {
    explicit HashTable(size_t capacity)
        : m_cap(capacity), m_table(m_cap, nullptr) {}

    ~HashTable() = default;  // The default destructor

    // mutable methods:

    // Clear all entries in hash table
    void clear(void) {
        for (auto &entry : m_table) entry = nullptr;
    }

    // Retrieve the entry value at `key` in hash table
    std::optional<int> get(const char *key) {
        uint64_t index = fnv1a_hash(key);
        auto cur_entry = m_table[index].get();
        while (cur_entry != nullptr) {
            if (std::strcmp(cur_entry->key, key) == 0) return cur_entry->val;
            cur_entry = cur_entry->next.get();
        }
        return std::nullopt;  // Key not found
    }

    // Insert value `val` in hash table at an index computed via hashing `key`
    // with `fnv1a` algorithm
    void insert(const char *key, const int val) {
        uint64_t index = fnv1a_hash(key);
        auto entry = std::make_shared<Entry>(key, val);
        index = linear_probe(key, index);
        if (m_table[index] == nullptr)  // Key not found, insert new entry
            m_table[index] = entry;     // Insert success
        else
            m_table[index]->val = val;  // Update success
    }

    void remove(const char *key) {  //    TODO
        return;
    }

    // immutable methods:

    size_t capacity(void) const { return m_cap; }

    // Check for the existence of a key without retrieving its value
    bool contains(const char *key) { return this->get(key).has_value(); }

    // Check if the hash table is empty
    bool is_empty(void) const {  // return this->size() == 0;
        for (const auto &entry : m_table) {
            if (entry != nullptr) return false;
        }
        return true;
    }

    // Return count of entries in hash table
    size_t size(void) const {
        size_t count = 0;
        for (const auto &entry : m_table) {
            auto cur = entry.get();
            while (cur != nullptr) {
                count += 1;
                cur = cur->next.get();
            }
        }
        return count;
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
        return (hash % m_cap);
    }

    // `djb2` Bernstein hash function iterates through each character,
    // left-shifting the current hash by 5 bits and adding the ASCII value.
    uint64_t djb2_hash(const char *key) {
        uint64_t hash = 5381;
        while (*key != '\0')  // hash * 33 + c;
            hash = (((hash << 5) + hash) + *key++);
        return (hash % m_cap);
    }

    uint64_t linear_probe(const char *key, uint64_t index) {
        auto step = 1;
        while (m_table[index] != nullptr) {
            if (std::strcmp(m_table[index]->key, key) == 0)
                return index;                  // Key already exists
            index = ((index + step) % m_cap);  // Move to the next slot
        }
        return index;
    }

    // data structures:

    struct Entry {
        const char *key;
        int val;
        std::shared_ptr<Entry> next;

        explicit Entry(const char *k, int v) : key(k), val(v), next(nullptr) {}
    };

    // members:

    const size_t m_cap;

    std::vector<std::shared_ptr<Entry>> m_table;
};

void print_result(const char *key, std::optional<int> result) {
    if (result.has_value())
        std::cout << "Count of " << key << ": " << result.value() << '\n';
    else
        std::cout << "Key '" << key << "' not found" << '\n';
}

int main(void) {
    constexpr size_t hashtable_capacity = 40;
    std::vector<std::pair<const char *, int>> keyval_pairs;

    HashTable ht(hashtable_capacity);  // Initialize the hash table
    keyval_pairs = {{"puppy", 5}, {"kitty", 8}, {"horsie", 12}};

    for (const auto &kv : keyval_pairs)  // Insert some key-value pairs
        ht.insert(kv.first, kv.second);
    ht.insert("puppy", 7);  // Update a key

    std::cout << "Size: " << ht.size() << '\n';
    std::cout << "Capacity: " << ht.capacity() << '\n';
    std::cout << "Is empty: " << ht.is_empty() << '\n';

    for (const auto &kv : keyval_pairs)  // Retrieve values
        print_result(kv.first, ht.get(kv.first));
    print_result("wolfie", ht.get("wolfie"));  // Key 'wolfie' not found

    ht.clear();  // Clear all key value entries
    std::cout << "Size: " << ht.size() << '\n';
    std::cout << "Capacity: " << ht.capacity() << '\n';
    std::cout << "Is empty: " << ht.is_empty() << '\n';
    print_result("puppy", ht.get("puppy"));  // Key 'puppy' not found

    return 0;
}
