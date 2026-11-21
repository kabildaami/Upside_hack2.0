import React from 'react';

export default function GameRenderer({ game, onAnswer }) {
  if (!game) {
    return <div>No game available</div>;
  }

  return (
    <div className="game-renderer">
      <div className="question">{game.question}</div>
      <div className="choices">
        {game.choices && game.choices.map((choice, idx) => (
          <button
            key={idx}
            className="choice-btn"
            onClick={() => onAnswer(idx)}
          >
            {choice}
          </button>
        ))}
      </div>
    </div>
  );
}
