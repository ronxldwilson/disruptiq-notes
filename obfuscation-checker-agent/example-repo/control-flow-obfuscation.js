// CONTROL FLOW OBFUSCATION

// 1. Dead code insertion
function deadCode() {
    var result = 0;
    if (false) { // never executed
        result = 999;
        console.log("This never runs");
    }
    result = 42;
    if (true) {
        result = result + 1;
    }
    // More dead code
    if (0 === 1) {
        var unused = "dead";
        console.log(unused);
    }
    return result;
}

// 2. Opaque predicates (always true/false conditions)
function opaquePredicate(x) {
    var condition = (x * 0) === 0; // always true
    if (condition) {
        return x + 1;
    } else {
        return x - 1; // never reached
    }
}

// 3. Control flow flattening
function flattenedControlFlow(input) {
    var state = 0;
    var result = 0;

    while (true) {
        switch (state) {
            case 0:
                if (input > 10) {
                    state = 1;
                } else {
                    state = 2;
                }
                break;
            case 1:
                result = input * 2;
                state = 3;
                break;
            case 2:
                result = input * 3;
                state = 3;
                break;
            case 3:
                return result;
        }
    }
}

// 4. Exception-based control flow
function exceptionControlFlow() {
    try {
        throw "goto";
    } catch (e) {
        if (e === "goto") {
            return 42;
        }
    }
}

// 5. Loop obfuscation with break/continue
function loopObfuscation() {
    var result = 0;
    for (var i = 0; i < 100; i++) {
        if (i < 10) continue;
        if (i > 20) break;
        if (i % 2 === 0) {
            result += i;
        } else {
            // dead code in loop
            var temp = i * 2;
        }
    }
    return result;
}

// 6. Nested conditionals with dead branches
function nestedDeadCode(x, y, z) {
    if (x > 0) {
        if (y > 0) {
            if (z > 0) {
                return x + y + z;
            } else if (false) {
                return x + y; // dead
            }
        } else if (0 === 1) {
            return x; // dead
        }
    } else if (Math.PI === 3.14) { // always false
        return 0; // dead
    }
    return x * y * z;
}

// 7. Goto simulation with labels (if supported)
function gotoSimulation() {
    var i = 0;
    start:
    if (i < 10) {
        console.log(i);
        i++;
        goto start; // simulated goto
    }
}

// 8. State machine with unnecessary states
function unnecessaryStates(input) {
    var state = "init";
    var result = input;

    while (state !== "end") {
        switch (state) {
            case "init":
                state = "process";
                break;
            case "process":
                result = result * 2;
                state = "validate";
                break;
            case "validate":
                if (result > 100) {
                    state = "adjust";
                } else {
                    state = "finalize";
                }
                break;
            case "adjust":
                result = result - 50;
                state = "finalize";
                break;
            case "finalize":
                state = "end";
                break;
            default:
                state = "error"; // dead state
        }
    }
    return result;
}
