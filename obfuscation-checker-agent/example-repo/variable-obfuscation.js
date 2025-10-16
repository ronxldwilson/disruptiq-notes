// VARIABLE AND FUNCTION NAME OBFUSCATION

// 1. Single character variables
var a = 1, b = 2, c = 3, d = a + b + c;
function f(x) { return x * 2; }
console.log(f(d));

// 2. Meaningless names
var qwerty = "password";
var asdfgh = "username";
var zxcvbn = qwerty + asdfgh;

// 3. Random character sequences
var aBcDeFgHiJkLmNoPqRsTuVwXyZ = 42;
var _0x1a2b3c4d5e6f = "secret";
var $$_aaBBcc = function() { return _0x1a2b3c4d5e6f; };

// 4. Numbers in variable names
var var1 = "test", var2 = "ing", var123 = var1 + var2;

// 5. Underscore patterns
var ___var___ = "value";
var _a_b_c_d_e_ = 123;

// 6. Mixed case nonsense
var VaR = "test", vAr = "case", vaR = "mix";

// 7. Function with obfuscated parameters
function func(param1, param2, param3) {
    var localVar1 = param1;
    var localVar2 = param2;
    var localVar3 = param3;
    return localVar1 + localVar2 + localVar3;
}

// 8. Class with obfuscated properties
class Cls {
    constructor() {
        this.propA = 1;
        this.propB = 2;
        this.propC = 3;
    }
    methodX() { return this.propA; }
    methodY() { return this.propB; }
    methodZ() { return this.propC; }
}

// 9. Obfuscated module exports
var module123 = {
    func1: function() { return "export1"; },
    func2: function() { return "export2"; },
    data1: "value1",
    data2: "value2"
};

// 10. Variable name collision (same name different scopes)
function collision() {
    var x = 1;
    if (true) {
        var x = 2; // same name, different value
        console.log(x); // 2
    }
    console.log(x); // 2 (hoisted)
}
