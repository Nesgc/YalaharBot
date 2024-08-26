import React, { useState, useEffect } from 'react';
import axios from 'axios';

function CharacterManager() {
  const [characters, setCharacters] = useState([]);
  const [newCharacterName, setNewCharacterName] = useState('');

  useEffect(() => {
    fetchCharacters();
  }, []);

  async function fetchCharacters() {
    try {
      const response = await axios.get('/api/characters/');
      setCharacters(response.data);
    } catch (error) {
      console.error('Error fetching characters:', error);
    }
  }

  async function addCharacter(e) {
    e.preventDefault();
    try {
      await axios.post('/api/characters/', { name: newCharacterName });
      setNewCharacterName('');
      fetchCharacters();
    } catch (error) {
      console.error('Error adding character:', error);
    }
  }

  return (
    <div>
      <h2>Character Manager</h2>
      <form onSubmit={addCharacter}>
        <input 
          type="text" 
          value={newCharacterName} 
          onChange={(e) => setNewCharacterName(e.target.value)} 
          placeholder="New character name" 
        />
        <button type="submit">Add Character</button>
      </form>
      <ul>
        {characters.map(char => (
          <li key={char.id}>{char.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default CharacterManager;