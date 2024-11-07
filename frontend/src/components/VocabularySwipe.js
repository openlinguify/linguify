import React, { useRef } from 'react';
import TinderCard from 'react-tinder-card';

const VocabularySwipe = ({ words }) => {
  const cardsRef = useRef(null); // A reference for the container div

  const onSwipe = (direction, word) => {
    console.log(`You swiped ${direction} on: ${word}`);
    // Handle swipe logic here
  };

  const onCardLeftScreen = (word) => {
    console.log(`${word} left the screen!`);
    // Handle card leaving the screen
  };

  if (!words || words.length === 0) {
    return <p>No words available for swipe.</p>;
  }

  return (
    <div ref={cardsRef} className="swipe-container">
      {words.map((word, index) => (
        <TinderCard
          key={index}
          onSwipe={(direction) => onSwipe(direction, word.word)}
          onCardLeftScreen={() => onCardLeftScreen(word.word)}
          preventSwipe={['up', 'down']} // Prevent vertical swipes
        >
          <div className="word-card">
            <h2>{word.word}</h2>
            <p>{word.translation}</p>
          </div>
        </TinderCard>
      ))}
    </div>
  );
};

export default VocabularySwipe;
