// STRING OBFUSCATION TECHNIQUES

// 1. Base64 encoding
var encoded = "SGVsbG8gV29ybGQ="; // "Hello World" in base64
var decoded = atob(encoded);
console.log(decoded);

// 2. Hex encoding
var hexString = "\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64"; // "Hello World" in hex
console.log(hexString);

// 3. Octal encoding
var octalString = "\110\145\154\154\157\40\127\157\162\154\144"; // "Hello World" in octal
console.log(octalString);

// 4. Unicode escapes
var unicodeStr = "\u0048\u0065\u006c\u006c\u006f\u0020\u0057\u006f\u0072\u006c\u0064";
console.log(unicodeStr);

// 5. String concatenation
var part1 = "Hell";
var part2 = "o Wo";
var part3 = "rld";
console.log(part1 + part2 + part3);

// 6. String from char codes
var str = String.fromCharCode(72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100);
console.log(str);

// 7. Template literal obfuscation
var a = "Wor", b = "ld";
console.log(`Hell${"o"} ${a + b}`);

// 8. Nested encoding (base64 of hex)
var doubleEncoded = "XHg0OFx4NjVceDY0XHg2NFx4NjdceDIwXHg1N1x4NmZceDcyXHg2Y1x4NjQ="; // base64 of hex string
console.log(atob(doubleEncoded));

// 9. Rot13 style encoding
function rot13(str) {
    return str.replace(/[a-zA-Z]/g, function(c) {
        return String.fromCharCode((c <= "Z" ? 90 : 122) >= (c = c.charCodeAt(0) + 13) ? c : c - 26);
    });
}
console.log(rot13("Uryyb Jbeyq"));

// 10. XOR encoding
function xorEncode(str, key) {
    var result = "";
    for (var i = 0; i < str.length; i++) {
        result += String.fromCharCode(str.charCodeAt(i) ^ key);
    }
    return result;
}
var xorStr = xorEncode("Hello World", 42);
console.log(xorEncode(xorStr, 42)); // decode
