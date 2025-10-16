# CONTROL FLOW OBFUSCATION

# 1. Dead code insertion
def dead_code():
    result = 0
    if False:  # never executed
        result = 999
        print("This never runs")
    result = 42
    if True:
        result = result + 1
    # More dead code
    if 0 == 1:
        unused = "dead"
        print(unused)
    return result

# 2. Opaque predicates
def opaque_predicate(x):
    condition = (x * 0) == 0  # always true
    if condition:
        return x + 1
    else:
        return x - 1  # never reached

# 3. Control flow flattening
def flattened_control_flow(input_val):
    state = 0
    result = 0

    while True:
        if state == 0:
            if input_val > 10:
                state = 1
            else:
                state = 2
        elif state == 1:
            result = input_val * 2
            state = 3
        elif state == 2:
            result = input_val * 3
            state = 3
        elif state == 3:
            return result

# 4. Exception-based control flow
def exception_control_flow():
    try:
        raise ValueError("goto")
    except ValueError as e:
        if str(e) == "goto":
            return 42

# 5. Complex conditional chains with dead branches
def nested_dead_code(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            elif False:
                return x + y  # dead
        elif 0 == 1:
            return x  # dead
    elif 3.14159 == 3.14:  # always false
        return 0  # dead
    return x * y * z

# 6. Loop with complex conditions and dead code
def loop_obfuscation():
    result = 0
    for i in range(100):
        if i < 10:
            continue
        if i > 20:
            break
        if i % 2 == 0:
            result += i
        else:
            # dead code in loop
            temp = i * 2
    return result

# 7. State machine with unnecessary states
def unnecessary_states(input_val):
    state = "init"
    result = input_val

    while state != "end":
        if state == "init":
            state = "process"
        elif state == "process":
            result = result * 2
            state = "validate"
        elif state == "validate":
            if result > 100:
                state = "adjust"
            else:
                state = "finalize"
        elif state == "adjust":
            result = result - 50
            state = "finalize"
        elif state == "finalize":
            state = "end"
        else:
            state = "error"  # dead state

    return result

# 8. Recursive function with dead recursion paths
def recursive_obfuscation(n, path="main"):
    if n <= 0:
        return 0
    if path == "dead":  # never taken
        return recursive_obfuscation(n - 1, "deader")
    elif path == "deader":  # never taken
        return n * 100
    else:
        return n + recursive_obfuscation(n - 1, "main")

# 9. Generator with dead yields
def generator_obfuscation():
    yield 1
    if False:
        yield 2  # dead
    yield 3
    if 0 == 1:
        yield 4  # dead
    yield 5

# 10. Context manager with dead code
class DeadCodeContext:
    def __enter__(self):
        if False:  # dead
            print("Never entered")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if False:  # dead
            print("Never exited")
        return False

def context_obfuscation():
    with DeadCodeContext():
        return 42
