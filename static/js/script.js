class FlashcardApp {
  constructor() {
    this.flashcards = [];
    this.currentCardIndex = 0;
    this.isFlipped = false;
    this.toastContainer = null;

    this.initializeToastContainer();
    this.initializeEventListeners();
    this.loadSavedFlashcards();
    this.loadTopics();
  }

  initializeToastContainer() {
    this.toastContainer = document.getElementById("toast-container");
    if (!this.toastContainer) {
      this.toastContainer = document.createElement("div");
      this.toastContainer.id = "toast-container";
      this.toastContainer.className = "toast-container";
      document.body.appendChild(this.toastContainer);
    }
  }

  async loadTopics() {
    try {
      const response = await fetch("/get_flashcards");
      const data = await response.json();

      if (response.ok && data.flashcards) {
        const topics = [...new Set(data.flashcards.map((card) => card.topic))];
        const topicFilter = document.getElementById("topic-filter");

        topicFilter.innerHTML = '<option value="">All Topics</option>';

        topics.forEach((topic) => {
          if (topic) {
            const option = document.createElement("option");
            option.value = topic;
            option.textContent = topic;
            topicFilter.appendChild(option);
          }
        });
      }
    } catch (error) {
      console.error("Error loading topics:", error);
    }
  }

  initializeEventListeners() {
    document
      .getElementById("generate-btn")
      .addEventListener("click", () => this.generateFlashcards());

    document
      .getElementById("prev-btn")
      .addEventListener("click", () => this.previousCard());

    document
      .getElementById("next-btn")
      .addEventListener("click", () => this.nextCard());

    document
      .getElementById("shuffle-btn")
      .addEventListener("click", () => this.shuffleCards());

    document
      .getElementById("reset-btn")
      .addEventListener("click", () => this.resetCards());

    document
      .getElementById("load-saved-btn")
      .addEventListener("click", () => this.loadSavedFlashcards());

    document
      .getElementById("topic-filter")
      .addEventListener("change", () => this.loadSavedFlashcards());

    // Keyboard navigation
    document.addEventListener("keydown", (e) => {
      const activeElement = document.activeElement;
      const isInputFocused =
        activeElement &&
        (activeElement.tagName === "INPUT" ||
          activeElement.tagName === "TEXTAREA" ||
          activeElement.contentEditable === "true" ||
          activeElement.isContentEditable);

      if (!isInputFocused && this.flashcards.length > 0) {
        switch (e.key) {
          case "ArrowLeft":
            e.preventDefault();
            this.previousCard();
            break;
          case "ArrowRight":
            e.preventDefault();
            this.nextCard();
            break;
          case " ":
          case "Enter":
            e.preventDefault();
            this.flipCurrentCard();
            break;
        }
      }
    });
  }

  async generateFlashcards() {
    const studyText = document.getElementById("study-text").value.trim();
    const topic = document.getElementById("topic").value.trim() || "General";

    if (!studyText) {
      this.showToast("Please enter some study notes first.", "error");
      return;
    }

    const generateBtn = document.getElementById("generate-btn");
    this.setLoadingState(generateBtn, true);

    try {
      const response = await fetch("/generate_flashcards", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: studyText, topic: topic }),
      });

      const data = await response.json();

      if (data.success && data.flashcards) {
        this.flashcards = data.flashcards;
        this.currentCardIndex = 0;
        this.displayFlashcards();
        this.showToast(
          `Generated ${data.flashcards.length} flashcards successfully!`,
          "success"
        );

        document.getElementById("study-text").value = "";
        document.getElementById("flashcards-section").style.display = "block";
        document
          .getElementById("flashcards-section")
          .scrollIntoView({ behavior: "smooth" });
      } else {
        throw new Error(data.error || "Failed to generate flashcards");
      }
    } catch (error) {
      console.error("Error generating flashcards:", error);
      this.showToast("Error generating flashcards. Please try again.", "error");
    } finally {
      this.setLoadingState(generateBtn, false);
    }
  }

  async loadSavedFlashcards() {
    const topic = document.getElementById("topic-filter").value || "";
    try {
      const response = await fetch(
        `/get_flashcards?topic=${encodeURIComponent(topic)}`
      );
      const data = await response.json();

      if (response.ok && data.flashcards && data.flashcards.length > 0) {
        this.flashcards = data.flashcards;
        this.currentCardIndex = 0;
        this.isFlipped = false;

        this.displayFlashcards();
        this.displaySavedFlashcards(data.flashcards);
        document.getElementById("flashcards-section").style.display = "block";

        this.showToast(
          `Loaded ${data.flashcards.length} flashcards from server`,
          "success"
        );
      } else {
        this.flashcards = [];
        document.getElementById("flashcards-section").style.display = "none";
        this.showToast("No flashcards found.", "info");
      }
    } catch (error) {
      console.error("Error loading flashcards:", error);
      this.showToast("Error loading flashcards.", "error");
    }
  }

  displayFlashcards() {
    if (this.flashcards.length === 0) {
      document.getElementById("flashcards-section").style.display = "none";
      return;
    }

    const flashcardContainer = document.getElementById("flashcard-container");
    const currentCard = this.flashcards[this.currentCardIndex];

    flashcardContainer.innerHTML = `
      <div class="flashcard ${this.isFlipped ? "flipped" : ""}" id="current-flashcard">
        <div class="flashcard-inner">
          <div class="flashcard-front">
            <div class="card-header">Question</div>
            <div class="card-content">${currentCard.question}</div>
            <div class="flip-hint">Click to reveal answer</div>
          </div>
          <div class="flashcard-back">
            <div class="card-header">Answer</div>
            <div class="card-content">${currentCard.answer}</div>
            <div class="flip-hint">Click to show question</div>
          </div>
        </div>
      </div>
    `;

    const flashcard = document.getElementById("current-flashcard");
    if (flashcard) {
      flashcard.addEventListener("click", () => this.flipCurrentCard());
      flashcard.style.cursor = "pointer";
    }

    document.getElementById("current-card").textContent =
      this.currentCardIndex + 1;
    document.getElementById("total-cards").textContent =
      this.flashcards.length;

    this.updateNavigationButtons();
  }

  flipCurrentCard() {
    this.isFlipped = !this.isFlipped;
    const flashcard = document.getElementById("current-flashcard");
    if (flashcard) {
      flashcard.classList.toggle("flipped", this.isFlipped);
    }
  }

  nextCard() {
    if (this.flashcards.length === 0) return;
    this.currentCardIndex = (this.currentCardIndex + 1) % this.flashcards.length;
    this.isFlipped = false;
    this.displayFlashcards();
  }

  previousCard() {
    if (this.flashcards.length === 0) return;
    this.currentCardIndex =
      this.currentCardIndex === 0
        ? this.flashcards.length - 1
        : this.currentCardIndex - 1;
    this.isFlipped = false;
    this.displayFlashcards();
  }

  shuffleCards() {
    if (this.flashcards.length === 0) {
      this.showToast("No flashcards to shuffle.", "error");
      return;
    }

    for (let i = this.flashcards.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.flashcards[i], this.flashcards[j]] = [
        this.flashcards[j],
        this.flashcards[i],
      ];
    }

    this.currentCardIndex = 0;
    this.isFlipped = false;
    this.displayFlashcards();
    this.showToast("Flashcards shuffled successfully!", "success");
  }

  resetCards() {
    this.currentCardIndex = 0;
    this.isFlipped = false;
    this.displayFlashcards();
    this.showToast("Reset to first card.", "success");
  }

  displaySavedFlashcards(flashcards) {
    const container = document.getElementById("saved-flashcards-container");

    if (!flashcards || flashcards.length === 0) {
      container.innerHTML = "<p>No saved flashcards found.</p>";
      return;
    }

    // Group flashcards by topic
    const groupedCards = flashcards.reduce((groups, card) => {
      const topic = card.topic || "General";
      if (!groups[topic]) groups[topic] = [];
      groups[topic].push(card);
      return groups;
    }, {});

    let html = "";
    Object.keys(groupedCards).forEach((topic) => {
      const cards = groupedCards[topic];
      html += `
        <div class="topic-section">
          <h3>${topic} (${cards.length} cards)</h3>
          <div class="saved-cards-grid">
            ${cards
              .map(
                (card, index) => `
              <div class="saved-card" data-topic="${topic}" data-index="${index}">
                <div class="saved-card-question">${card.question}</div>
                <div class="saved-card-meta">
                  <span class="difficulty ${card.difficulty}">${card.difficulty || "medium"}</span>
                  <button onclick="flashcardApp.loadSpecificCard('${topic}', ${index})" class="load-card-btn">Load</button>
                </div>
              </div>
            `
              )
              .join("")}
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  }

  loadSpecificCard(topic, cardIndex) {
    const topicCards = this.flashcards.filter(
      (card) => (card.topic || "General") === topic
    );
    if (topicCards.length > 0 && cardIndex < topicCards.length) {
      const globalIndex = this.flashcards.findIndex(
        (card) =>
          (card.topic || "General") === topic &&
          card.question === topicCards[cardIndex].question
      );

      if (globalIndex !== -1) {
        this.currentCardIndex = globalIndex;
        this.isFlipped = false;
        this.displayFlashcards();
        document.getElementById("flashcards-section").style.display = "block";
        document
          .getElementById("flashcards-section")
          .scrollIntoView({ behavior: "smooth" });
      }
    }
  }

  updateNavigationButtons() {
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    if (prevBtn && nextBtn) {
      if (this.flashcards.length <= 1) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
      } else {
        prevBtn.disabled = false;
        nextBtn.disabled = false;
      }
    }
  }

  setLoadingState(button, isLoading) {
    if (!button) return;

    if (isLoading) {
      button.disabled = true;
      button.innerHTML =
        '<span class="loading-spinner"></span> Generating...';
      button.classList.add("loading");
    } else {
      button.disabled = false;
      button.innerHTML = "Generate Flashcards";
      button.classList.remove("loading");
    }
  }

  showToast(message, type = "info", duration = 5000) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const icons = {
      success: "✅",
      error: "❌",
      warning: "⚠️",
      info: "ℹ️",
    };

    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;

    this.toastContainer.appendChild(toast);

    setTimeout(() => toast.classList.add("toast-show"), 10);

    setTimeout(() => {
      toast.classList.add("toast-hide");
      setTimeout(() => {
        if (toast.parentNode) toast.remove();
      }, 300);
    }, duration);

    const toasts = this.toastContainer.querySelectorAll(".toast");
    if (toasts.length > 5) toasts[0].remove();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.flashcardApp = new FlashcardApp();
});
