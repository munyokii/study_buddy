class FlashcardApp {
  constructor() {
    this.flashcards = [];
    this.currentCardIndex = 0;
    this.isFlipped = false;

    this.initializeEventListeners();
    this.loadSavedFlashcards();
  }

  initializeEventListeners() {
    // Generating flashcards button
    document.getElementById('generate-btn').addEventListener('click', () => {
      this.generateFlashcards();
    });

    // Navigation buttons
    document.getElementById('prev-btn').addEventListener('click', () => {
      this.previousCard();
    });

    document.getElementById('next-btn').addEventListener('click', () => {
      this.nextCard();
    });

    // Control buttons
    document.getElementById('shuffle-btn').addEventListener('click', () => {
      this.shuffleCards();
    });

    document.getElementById('reset-btn').addEventListener('click', () => {
      this.resetCards();
    });

    // Loading saved flashcards
    document.getElementById('load-saved-btn').addEventListener('click', () => {
      this.loadSavedFlashcards();
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (this.flashcards.length > 0) {
        switch(e.key) {
          case 'ArrowLeft':
            this.previousCard();
            break;
          case 'ArrowRight':
            this.nextCard();
            break;
          case ' ':
          case 'Enter':
            e.preventDefault();
            this.flipCurrentCard();
            break;
        }
      }
    });
  }
}