/*
 * C++ file with intentional issues for cppcheck testing.
 */

#include <iostream>
#include <string>
#include <vector>
#include <memory>

class VulnerableClass {
private:
    int* data;
    std::string name;

public:
    // Issue: no initialization in constructor
    VulnerableClass() {
        // Issue: data pointer not initialized
    }

    // Issue: memory leak in destructor
    ~VulnerableClass() {
        // Issue: no cleanup of data pointer
    }

    // Issue: buffer overflow
    void setName(const char* input) {
        // Issue: no bounds checking for strcpy
        strcpy((char*)name.c_str(), input);
    }

    // Issue: null pointer dereference
    void dangerousMethod() {
        if (data == nullptr) {
            // Issue: still dereferencing null pointer
            *data = 42;
        }
    }

    // Issue: unused parameter
    void unusedParameter(int param) {
        // Issue: param is not used
        std::cout << "Method called" << std::endl;
    }
};

// Issue: exception safety issues
void exception_unsafe() {
    int* ptr = new int[10];
    // Issue: if exception thrown here, memory leak
    throw std::runtime_error("Error");

    // This code never reached
    delete[] ptr;
}

// Issue: resource leak
void resource_leak() {
    FILE* fp = fopen("file.txt", "r");
    // Issue: no fclose if early return
    if (fp == nullptr) {
        return;  // Resource leak
    }
    // Issue: no fclose at end
}

// Issue: STL container issues
void stl_issues() {
    std::vector<int> vec;
    vec.reserve(10);

    // Issue: accessing invalid index
    vec[5] = 42;  // Vector only reserved, not resized

    // Issue: iterator invalidation
    auto it = vec.begin();
    vec.push_back(1);  // May invalidate iterator
    *it = 2;  // Iterator may be invalid
}

int main() {
    VulnerableClass obj;

    // Issue: using uninitialized object
    obj.dangerousMethod();

    try {
        exception_unsafe();
    } catch (const std::exception& e) {
        std::cout << "Caught: " << e.what() << std::endl;
    }

    resource_leak();
    stl_issues();

    return 0;
}
