/*
 * Complex C++ file with advanced issues for cppcheck testing.
 */

#include <iostream>
#include <thread>
#include <mutex>
#include <memory>
#include <string>
#include <vector>

// Issue: Race condition in multi-threading
class ThreadUnsafeClass {
private:
    int counter = 0;
    // Issue: no mutex for thread safety
    // std::mutex mtx;

public:
    void increment() {
        // Issue: race condition - no synchronization
        counter++;
    }

    int getCounter() {
        return counter;
    }
};

// Issue: Smart pointer misuse
void smart_pointer_issues() {
    // Issue: raw pointer in modern C++
    int* raw_ptr = new int(42);

    // Issue: not using smart pointers
    std::unique_ptr<int> smart_ptr(new int(42));

    // Issue: unnecessary raw pointer
    delete raw_ptr;

    // Issue: dangling reference
    int* dangling = smart_ptr.get();
    smart_ptr.reset();  // Now dangling points to freed memory
    *dangling = 100;    // Undefined behavior
}

// Issue: Exception safety in RAII
class RAIIExample {
private:
    int* resource1;
    std::string* resource2;

public:
    RAIIExample() : resource1(nullptr), resource2(nullptr) {
        resource1 = new int(0);
        resource2 = new std::string("test");

        // Issue: if exception thrown here, resources leak
        throw std::runtime_error("Construction failed");
    }

    ~RAIIExample() {
        delete resource1;
        delete resource2;
    }
};

// Issue: Template issues
template<typename T>
class TemplateIssues {
private:
    T* data;

public:
    TemplateIssues() : data(nullptr) {}

    // Issue: no copy constructor
    // Issue: no assignment operator

    // Issue: potential null dereference
    void process() {
        if (data) {
            *data = T();  // What if T has no default constructor?
        }
    }
};

// Issue: Inheritance issues
class Base {
public:
    virtual ~Base() = default;
    virtual void method() {
        std::cout << "Base" << std::endl;
    }
};

class Derived : public Base {
private:
    std::string data;

public:
    // Issue: no override keyword
    void method() {
        // Issue: not calling base class method
        std::cout << "Derived: " << data << std::endl;
    }

    // Issue: slicing problem
    void setData(const std::string& d) {
        data = d;
    }
};

// Issue: Function pointer misuse
typedef void (*FunctionPtr)(int);

void function1(int x) {
    std::cout << "Function1: " << x << std::endl;
}

void function2(int x) {
    std::cout << "Function2: " << x << std::endl;
}

void function_pointer_issues() {
    FunctionPtr fp = function1;

    // Issue: no null check
    fp(42);

    // Issue: type confusion
    fp = reinterpret_cast<FunctionPtr>(function2);
    fp(42);
}

// Issue: Const correctness
class ConstIssues {
private:
    mutable int mutable_counter;  // Issue: overuse of mutable
    int data;

public:
    ConstIssues() : mutable_counter(0), data(0) {}

    // Issue: const method modifying data via mutable
    void constMethod() const {
        mutable_counter++;  // This is allowed but questionable
    }

    // Issue: const method returning non-const reference
    int& getData() const {
        return const_cast<int&>(data);  // Dangerous
    }
};

int main() {
    // Test thread safety issues
    ThreadUnsafeClass thread_obj;
    std::thread t1([&]() { for(int i = 0; i < 1000; i++) thread_obj.increment(); });
    std::thread t2([&]() { for(int i = 0; i < 1000; i++) thread_obj.increment(); });
    t1.join();
    t2.join();
    std::cout << "Counter: " << thread_obj.getCounter() << std::endl;

    // Test smart pointer issues
    smart_pointer_issues();

    // Test RAII issues
    try {
        RAIIExample ra;
    } catch (const std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
    }

    // Test template issues
    TemplateIssues<int> ti;
    ti.process();

    // Test inheritance issues
    Derived d;
    d.setData("test");
    Base* b = &d;
    b->method();  // Slicing issue

    // Test function pointer issues
    function_pointer_issues();

    // Test const issues
    ConstIssues ci;
    ci.constMethod();
    int& ref = ci.getData();  // Dangerous
    ref = 42;

    return 0;
}
