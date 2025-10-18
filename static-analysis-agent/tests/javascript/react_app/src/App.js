/**
 * React App component with intentional issues.
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [data, setData] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [count, setCount] = useState(0);

  // Issue: unused import
  import('./utils').then(module => {
    console.log('Dynamic import');
  });

  // Issue: direct DOM manipulation in React
  useEffect(() => {
    document.title = 'My App';
  }, []);

  // Issue: eval usage (security vulnerability)
  const executeCode = (code) => {
    // Security issue: eval with user input
    return eval(code);
  };

  // Issue: XSS vulnerability
  const renderUserContent = () => {
    // Issue: dangerouslySetInnerHTML without sanitization
    return <div dangerouslySetInnerHTML={{ __html: userInput }} />;
  };

  // Issue: no error handling
  const fetchData = async () => {
    const response = await axios.get('/api/data');
    setData(response.data);
  };

  // Issue: missing key prop in map
  const renderList = () => {
    return data.map(item => (
      <div>{item.name}</div> // Missing key prop
    ));
  };

  // Issue: unused variable
  const unusedVariable = 'never used';

  // Issue: poor prop validation (no PropTypes)
  const UserComponent = ({ name, age }) => {
    return <div>{name} is {age} years old</div>;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>My React App</h1>

        {/* Issue: missing alt attribute */}
        <img src="logo.png" />

        {/* Issue: no form validation */}
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Enter HTML..."
        />

        <button onClick={() => executeCode(userInput)}>
          Execute Code
        </button>

        {renderUserContent()}

        <button onClick={fetchData}>
          Fetch Data
        </button>

        {data && renderList()}

        {/* Issue: inline function in render */}
        <button onClick={() => setCount(count + 1)}>
          Count: {count}
        </button>

        <UserComponent name="John" age={25} />
      </header>
    </div>
  );
}

export default App;
