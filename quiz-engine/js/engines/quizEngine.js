import { getTopicById, TOPICS, getAllQuestions } from '../data/topics.js';

export class QuizEngine {
  constructor() {
    this.currentTopicId = 'topic-1';
    this.questionPool = [];
    this.usedQuestionIds = new Set();
    this.currentQuestion = null;
    this.currentShuffledOptions = [];
    this.selectedOptionIndex = null;
    this.isAnswered = false;

    // Statistics
    this.stats = {
      totalAnswered: 0,
      correctCount: 0,
      incorrectCount: 0,
      streak: 0,
      bestStreak: 0,
      cycleIndex: 1
    };

    this.initTopic(this.currentTopicId);
  }

  /**
   * Set active topic and reinitialize question pool
   * @param {string} topicId
   */
  setTopic(topicId) {
    this.currentTopicId = topicId;
    this.initTopic(topicId);
  }

  initTopic(topicId) {
    let sourceQuestions = [];
    if (topicId === 'all') {
      sourceQuestions = getAllQuestions();
    } else {
      const topic = getTopicById(topicId);
      sourceQuestions = topic ? topic.questions : [];
    }

    this.questionPool = [...sourceQuestions];
    this.usedQuestionIds.clear();
    this.currentQuestion = null;
    this.selectedOptionIndex = null;
    this.isAnswered = false;
  }

  /**
   * Get total number of questions in active topic
   */
  getTotalTopicQuestions() {
    if (this.currentTopicId === 'all') return getAllQuestions().length;
    const topic = getTopicById(this.currentTopicId);
    return topic ? topic.questions.length : 0;
  }

  /**
   * Pick next random question ensuring no duplicates in current session cycle
   */
  nextQuestion() {
    let availableQuestions = this.questionPool.filter(q => !this.usedQuestionIds.has(q.id));

    // If all questions have been used, start a fresh random cycle
    if (availableQuestions.length === 0) {
      this.usedQuestionIds.clear();
      this.stats.cycleIndex++;
      availableQuestions = [...this.questionPool];
    }

    if (availableQuestions.length === 0) {
      return null;
    }

    // Pick random question
    const randomIndex = Math.floor(Math.random() * availableQuestions.length);
    const question = availableQuestions[randomIndex];

    this.usedQuestionIds.add(question.id);
    this.currentQuestion = question;
    this.selectedOptionIndex = null;
    this.isAnswered = false;

    // Shuffle options
    this.currentShuffledOptions = this.shuffleOptions(question.options, question.correctAnswer);

    return {
      question: this.currentQuestion,
      shuffledOptions: this.currentShuffledOptions,
      progress: {
        current: this.usedQuestionIds.size,
        total: this.questionPool.length,
        cycle: this.stats.cycleIndex
      }
    };
  }

  /**
   * Fisher-Yates Shuffle with tracking of correct answer
   */
  shuffleOptions(options, correctAnswer) {
    const letters = ['A', 'B', 'C', 'D', 'E'];
    const items = options.map(opt => ({
      text: opt,
      isCorrect: String(opt).trim() === String(correctAnswer).trim()
    }));

    // Random shuffle
    for (let i = items.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }

    return items.map((item, index) => ({
      letter: letters[index] || String.fromCharCode(65 + index),
      text: item.text,
      isCorrect: item.isCorrect
    }));
  }

  /**
   * Select an option index (0 to 4)
   */
  selectOption(index) {
    if (this.isAnswered) return false;
    if (index >= 0 && index < this.currentShuffledOptions.length) {
      this.selectedOptionIndex = index;
      return true;
    }
    return false;
  }

  /**
   * Submit the currently selected answer
   */
  submitAnswer() {
    if (this.selectedOptionIndex === null || this.isAnswered || !this.currentQuestion) {
      return null;
    }

    this.isAnswered = true;
    const selectedOption = this.currentShuffledOptions[this.selectedOptionIndex];
    const isCorrect = !!selectedOption.isCorrect;

    this.stats.totalAnswered++;
    if (isCorrect) {
      this.stats.correctCount++;
      this.stats.streak++;
      if (this.stats.streak > this.stats.bestStreak) {
        this.stats.bestStreak = this.stats.streak;
      }
    } else {
      this.stats.incorrectCount++;
      this.stats.streak = 0;
    }

    // Find correct option index in shuffled list
    const correctOptionIndex = this.currentShuffledOptions.findIndex(o => o.isCorrect);
    const correctOption = this.currentShuffledOptions[correctOptionIndex];

    return {
      isCorrect,
      selectedOption,
      selectedOptionIndex: this.selectedOptionIndex,
      correctOption,
      correctOptionIndex,
      correctAnswer: this.currentQuestion.correctAnswer,
      explanation: this.currentQuestion.explanation,
      ruleRef: this.currentQuestion.ruleRef,
      stats: this.getStats()
    };
  }

  /**
   * Get accuracy and stats
   */
  getStats() {
    const accuracy = this.stats.totalAnswered > 0
      ? Math.round((this.stats.correctCount / this.stats.totalAnswered) * 100)
      : 0;

    return {
      ...this.stats,
      accuracy
    };
  }

  resetStats() {
    this.stats = {
      totalAnswered: 0,
      correctCount: 0,
      incorrectCount: 0,
      streak: 0,
      bestStreak: 0,
      cycleIndex: 1
    };
    this.initTopic(this.currentTopicId);
  }
}
