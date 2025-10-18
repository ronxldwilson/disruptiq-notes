/**
 * Frontend JavaScript for fullstack app with issues.
 */

// Global variables - issue
let apiBaseUrl = 'http://localhost:5000/api';
let userData = null;

// Issue: no error handling
function fetchUsers() {
    const userId = document.getElementById('userId').value;

    // Issue: no input validation
    fetch(`${apiBaseUrl}/users?id=${userId}`)
        .then(response => response.json())
        .then(data => {
            // Issue: XSS vulnerability - direct innerHTML
            document.getElementById('users').innerHTML = JSON.stringify(data);
        });
}

// Issue: eval usage
function executeCode() {
    const code = document.getElementById('code').value;

    // Security issue: sending code to server for execution
    fetch(`${apiBaseUrl}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    })
    .then(response => response.json())
    .then(data => {
        // Issue: eval of server response
        const result = eval(data.output);
        document.getElementById('result').innerHTML = result;
    });
}

// Issue: no input validation
function loadFile() {
    const filename = document.getElementById('filename').value;

    fetch(`${apiBaseUrl}/files/${filename}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById('fileContent').innerHTML = data;
        });
}

// Issue: unused function
function unusedFrontendFunction() {
    return 'This is never called';
}

// Issue: poor event handling
document.addEventListener('DOMContentLoaded', function() {
    // Issue: no null checks
    document.getElementById('fetchUsersBtn').addEventListener('click', fetchUsers);
    document.getElementById('executeBtn').addEventListener('click', executeCode);
    document.getElementById('loadFileBtn').addEventListener('click', loadFile);
});

// Issue: global function pollution
function globalHelper() {
    console.log('Global helper function');
}
