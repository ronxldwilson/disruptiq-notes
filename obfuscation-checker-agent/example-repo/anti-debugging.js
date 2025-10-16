// Anti-debugging techniques

// 1. Debugger detection and removal
function detectDebugger() {
    var start = new Date();
    debugger; // This will pause execution if dev tools are open
    var end = new Date();
    if (end - start > 100) {
        // Debugger detected
        return true;
    }
    return false;
}

// 2. Self-defense mechanism
if (typeof console !== 'undefined') {
    console.clear = function() { return; }; // Disable console.clear
}

// 3. Timing-based detection
var timeStart = performance.now();
setTimeout(function() {
    var timeEnd = performance.now();
    if (timeEnd - timeStart > 110) { // Should be ~100ms
        // Likely being debugged
        document.body.innerHTML = "Debugging detected";
    }
}, 100);

// 4. Function redefinition to prevent inspection
var originalLog = console.log;
console.log = function() {
    // Check if being called from dev tools
    var stack = new Error().stack;
    if (stack && stack.indexOf('eval') !== -1) {
        return; // Don't log if from eval
    }
    return originalLog.apply(console, arguments);
};

// 5. Domain locking
var allowedDomains = ['example.com', 'trusted.com'];
if (allowedDomains.indexOf(window.location.hostname) === -1) {
    document.body.innerHTML = "Access denied";
    throw new Error("Unauthorized domain");
}

// 6. Source map removal simulation
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoibm9uZSJ9

// 7. Obfuscated anti-debugging
eval(atob("dmFyIGQ9bmV3IERhdGUoKTt2b2lkIDB8fChkLmdldFRpbWUoKS1kPjE1MD8oZG9jdW1lbnQuYm9keS5pbm5lckhUTUw9J0RlYnVnZ2luZyBkZXRlY3RlZCcsc3RvcCgpKTp2b2lkIDA="));
