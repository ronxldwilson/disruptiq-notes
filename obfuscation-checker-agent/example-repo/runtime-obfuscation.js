// RUNTIME OBFUSCATION TECHNIQUES

// 1. Eval usage
var code = "console.log('Hello from eval!');";
eval(code);

// 2. Function constructor
var func = new Function("a", "b", "return a + b;");
console.log(func(5, 3));

// 3. setTimeout/setInterval obfuscation
setTimeout("console.log('Delayed execution');", 1000);

// 4. Dynamic function creation
function createFunction(body) {
    return new Function(body);
}
var dynamicFunc = createFunction("return 'dynamic';");
console.log(dynamicFunc());

// 5. Dynamic property access
var obj = { secret: "hidden" };
var prop = "sec" + "ret";
console.log(obj[prop]);

// 6. Dynamic module loading simulation
function loadModule(name) {
    var modules = {
        "math": { add: function(a,b) { return a+b; } },
        "string": { upper: function(s) { return s.toUpperCase(); } }
    };
    return modules[name];
}
var math = loadModule("math");
console.log(math.add(2, 3));

// 7. Obfuscated require/import simulation
var require = function(module) {
    var modules = {
        "fs": { readFile: function() { return "file content"; } },
        "crypto": { hash: function() { return "hashed"; } }
    };
    return modules[module] || {};
};

// 8. Runtime string decryption
function decryptString(encrypted, key) {
    var result = "";
    for (var i = 0; i < encrypted.length; i++) {
        result += String.fromCharCode(encrypted.charCodeAt(i) ^ key);
    }
    return result;
}
var encrypted = "KRYE"; // "HELP" XORed with key 42
console.log(decryptString(encrypted, 42));

// 9. Self-modifying code (simulation)
function selfModifying() {
    var code = "return 42;";
    // Modify the function at runtime
    selfModifying = new Function(code);
    return selfModifying();
}

// 10. Proxy-based obfuscation
var handler = {
    get: function(target, prop) {
        if (prop in target) {
            return target[prop];
        }
        return "obfuscated_" + prop;
    }
};
var obfuscatedObj = new Proxy({}, handler);
console.log(obfuscatedObj.anyProperty);

// 11. Symbol-based property hiding
var hiddenSymbol = Symbol("hidden");
var objWithHidden = {};
objWithHidden[hiddenSymbol] = "secret";
console.log(Object.keys(objWithHidden)); // won't show symbol

// 12. WeakMap for hidden storage
var weakMap = new WeakMap();
var key = {};
weakMap.set(key, "hidden data");
console.log(weakMap.get(key));

// 13. Runtime code generation with template literals
function generateCode(params) {
    var template = `
        function generated() {
            var result = 0;
            ${params.operations.join('\n            ')}
            return result;
        }
        return generated;
    `;
    return eval(template);
}

var operations = ["result += 1;", "result *= 2;", "result += 10;"];
var generatedFunc = generateCode({operations: operations});
console.log(generatedFunc());
