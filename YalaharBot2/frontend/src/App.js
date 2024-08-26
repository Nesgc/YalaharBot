import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import CharacterManager from './components/CharacterManager';
import Home from './components/Home';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/characters">Characters</Link></li>
          </ul>
        </nav>

        <Routes>
          <Route path="/characters" element={<CharacterManager />} />
          <Route path="/" element={<Home />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;