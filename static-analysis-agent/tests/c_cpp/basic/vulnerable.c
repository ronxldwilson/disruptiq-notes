/*
 * C file with intentional security and quality issues for cppcheck testing.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Issue: buffer overflow vulnerability
void vulnerable_function(char *input) {
    char buffer[10];
    // Issue: no bounds checking
    strcpy(buffer, input);  // Buffer overflow potential
    printf("Buffer: %s\n", buffer);
}

// Issue: null pointer dereference
void null_pointer_issue() {
    int *ptr = NULL;
    // Issue: dereferencing null pointer
    *ptr = 42;  // This will crash
}

// Issue: uninitialized variable
void uninitialized_var() {
    int x;
    // Issue: using uninitialized variable
    printf("Value: %d\n", x);
}

// Issue: memory leak
void memory_leak() {
    // Issue: malloc without free
    int *data = (int*)malloc(sizeof(int) * 10);
    // Memory leak - no free(data)
}

// Issue: division by zero
void division_by_zero(int divisor) {
    int result;
    // Issue: no check for divisor == 0
    result = 100 / divisor;
    printf("Result: %d\n", result);
}

// Issue: array out of bounds
void array_bounds() {
    int arr[5] = {1, 2, 3, 4, 5};
    // Issue: accessing beyond array bounds
    printf("Out of bounds: %d\n", arr[10]);
}

// Issue: unused variable
void unused_variable() {
    int unused = 42;
    // Issue: variable declared but never used
    printf("Hello\n");
}

// Issue: poor error handling
FILE* open_file(char *filename) {
    // Issue: no error checking
    FILE *fp = fopen(filename, "r");
    return fp;  // May return NULL
}

int main(int argc, char *argv[]) {
    // Issue: no argument validation
    if (argc > 1) {
        vulnerable_function(argv[1]);
    }

    null_pointer_issue();
    uninitialized_var();
    memory_leak();
    division_by_zero(0);
    array_bounds();
    unused_variable();

    FILE *fp = open_file("nonexistent.txt");
    // Issue: no null check
    fscanf(fp, "%s", buffer);

    return 0;
}
