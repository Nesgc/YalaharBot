import React, { useState, useEffect } from 'react';
import axios from 'axios';

function CharacterManager() {
  const [characters, setCharacters] = useState([]);
  const [discordUsers, setDiscordUsers] = useState([]);
  const [newCharacter, setNewCharacter] = useState({
    name: '',
    accountid: '',
    level: 1,
    vocation: '',
    world: ''
  });

  useEffect(() => {
    fetchCharacters();
    fetchDiscordUsers();
  }, []);

  async function fetchCharacters() {
    try {
      const response = await axios.get('/api/characters/');
      setCharacters(response.data);
    } catch (error) {
      console.error('Error fetching characters:', error);
    }
  }

  async function fetchDiscordUsers() {
    try {
      const response = await axios.get('/api/discord-users/');
      setDiscordUsers(response.data);
    } catch (error) {
      console.error('Error fetching Discord users:', error);
    }
  }

  async function addCharacter(e) {
    e.preventDefault();
    try {
      await axios.post('/api/characters/', newCharacter);
      setNewCharacter({ name: '', accountid: '', level: 1, vocation: '', world: '' });
      fetchCharacters();
    } catch (error) {
      console.error('Error adding character:', error);
    }
  }

  return (
    <div>
      <h2>Character Manager</h2>
      <div className="bg-blue-500 text-white p-4">
  This is a Tailwind CSS component2!
</div>

      <form onSubmit={addCharacter}>
        <input 
          type="text" 
          value={newCharacter.name} 
          onChange={(e) => setNewCharacter({...newCharacter, name: e.target.value})} 
          placeholder="Character name" 
        />
        <select
          value={newCharacter.accountid}
          onChange={(e) => setNewCharacter({...newCharacter, accountid: e.target.value})}
        >
          <option value="">Select Discord User</option>
          {discordUsers.map(user => (
            <option key={user.id} value={user.id}>{user.User}</option>
          ))}
        </select>
        <input 
          type="number" 
          value={newCharacter.level} 
          onChange={(e) => setNewCharacter({...newCharacter, level: parseInt(e.target.value)})} 
          placeholder="Level" 
        />
        <input 
          type="text" 
          value={newCharacter.vocation} 
          onChange={(e) => setNewCharacter({...newCharacter, vocation: e.target.value})} 
          placeholder="Vocation" 
        />
        <input 
          type="text" 
          value={newCharacter.world} 
          onChange={(e) => setNewCharacter({...newCharacter, world: e.target.value})} 
          placeholder="World" 
        />
        <button type="submit">Add Character</button>
      </form>
      <ul>
        {characters.map(char => (
          <li key={char.id}>{char.name} - Level {char.level} {char.vocation} in {char.world}</li>
        ))}
      </ul>
    </div>
  );
}

export default CharacterManager;