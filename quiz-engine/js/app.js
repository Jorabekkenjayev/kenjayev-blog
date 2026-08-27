import { QuizEngine } from './engines/quizEngine.js';
import { FormulaEngine } from './engines/formulaEngine.js';
import { DiagramRenderer } from './engines/diagramRenderer.js';
import { TOPICS } from './data/topics.js';

class QuizApp {
  constructor() {
    this.quizEngine = new QuizEngine();
    this.formulaEngine = new FormulaEngine();
    this.currentTopicId = 'topic-1';
    this.initElements();
    this.initEventListeners();
    this.loadQuestion();
    this.updateStats();
  }

  initElements() {
    // Topic Selector & Navigation
    this.topicSelect = document.getElementById('topicSelect');
    this.btnFormula = document.getElementById('btnFormula');
    this.btnThemeToggle = document.getElementById('btnThemeToggle');

    // Stats
    this.statAnswered = document.getElementById('statAnswered');
    this.statCorrect = document.getElementById('statCorrect');
    this.statIncorrect = document.getElementById('statIncorrect');
    this.statAccuracy = document.getElementById('statAccuracy');
    this.statStreak = document.getElementById('statStreak');

    // Quiz Card
    this.quizCard = document.getElementById('quizCard');
    this.topicBadge = document.getElementById('topicBadge');
    this.questionProgress = document.getElementById('questionProgress');
    this.questionText = document.getElementById('questionText');
    this.diagramContainer = document.getElementById('diagramContainer');
    this.optionsContainer = document.getElementById('optionsContainer');
    this.feedbackContainer = document.getElementById('feedbackContainer');

    // Actions
    this.btnSubmit = document.getElementById('btnSubmit');
    this.btnNext = document.getElementById('btnNext');

    // Formula Modal
    this.formulaModal = document.getElementById('formulaModal');
    this.btnCloseModal = document.getElementById('btnCloseModal');
    this.formulaTitle = document.getElementById('formulaTitle');
    this.formulaCategory = document.getElementById('formulaCategory');
    this.formulaDisplay = document.getElementById('formulaDisplay');
    this.formulaRuleText = document.getElementById('formulaRuleText');
    this.formulaSymbols = document.getElementById('formulaSymbols');
    this.btnPrevFormula = document.getElementById('btnPrevFormula');
    this.btnRandomFormula = document.getElementById('btnRandomFormula');
    this.btnNextFormula = document.getElementById('btnNextFormula');
  }

  initEventListeners() {
    // Topic Change
    this.topicSelect.addEventListener('change', (e) => {
      this.currentTopicId = e.target.value;
      this.quizEngine.setTopic(this.currentTopicId);
      this.quizEngine.resetStats();
      this.updateStats();
      this.loadQuestion();
    });

    // Theme toggle
    this.btnThemeToggle.addEventListener('click', () => {
      const isLight = document.body.getAttribute('data-theme') === 'light';
      document.body.setAttribute('data-theme', isLight ? 'dark' : 'light');
      this.btnThemeToggle.textContent = isLight ? '🌙' : '☀️';
    });

    // Quiz Actions
    this.btnSubmit.addEventListener('click', () => this.handleAnswerSubmit());
    this.btnNext.addEventListener('click', () => this.loadQuestion());

    // Formula Modal Events
    this.btnFormula.addEventListener('click', () => this.openFormulaModal());
    this.btnCloseModal.addEventListener('click', () => this.closeFormulaModal());
    this.formulaModal.addEventListener('click', (e) => {
      if (e.target === this.formulaModal) this.closeFormulaModal();
    });

    this.btnPrevFormula.addEventListener('click', () => {
      const rule = this.formulaEngine.getPrevFormula(this.currentTopicId);
      this.renderFormulaDetails(rule);
    });

    this.btnNextFormula.addEventListener('click', () => {
      const rule = this.formulaEngine.getNextFormula(this.currentTopicId);
      this.renderFormulaDetails(rule);
    });

    this.btnRandomFormula.addEventListener('click', () => {
      const rule = this.formulaEngine.getRandomFormula(this.currentTopicId);
      this.renderFormulaDetails(rule);
    });

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
      if (this.formulaModal.classList.contains('open')) {
        if (e.key === 'Escape') this.closeFormulaModal();
        if (e.key === 'ArrowLeft') this.btnPrevFormula.click();
        if (e.key === 'ArrowRight') this.btnNextFormula.click();
        if (e.key.toLowerCase() === 'r') this.btnRandomFormula.click();
        return;
      }

      if (e.key.toLowerCase() === 'f') {
        this.openFormulaModal();
        return;
      }

      const keyIndexMap = { '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, 'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4 };
      const lowerKey = e.key.toLowerCase();
      if (lowerKey in keyIndexMap && !this.quizEngine.isAnswered) {
        this.selectOption(keyIndexMap[lowerKey]);
        return;
      }

      if (e.key === 'Enter') {
        if (!this.quizEngine.isAnswered && this.quizEngine.selectedOptionIndex !== null) {
          this.handleAnswerSubmit();
        } else if (this.quizEngine.isAnswered) {
          this.loadQuestion();
        }
      }

      if (e.code === 'Space' && this.quizEngine.isAnswered) {
        e.preventDefault();
        this.loadQuestion();
      }
    });
  }

  loadQuestion() {
    const data = this.quizEngine.nextQuestion();
    if (!data) return;

    const { question, shuffledOptions, progress } = data;

    // Reset card animation
    this.quizCard.classList.remove('card-anim-slide-in');
    void this.quizCard.offsetWidth; // trigger reflow
    this.quizCard.classList.add('card-anim-slide-in');

    // Update Header Metadata
    this.topicBadge.textContent = question.topicTitle || 'Burchaklar';
    this.questionProgress.textContent = `Savol ${progress.current} / ${progress.total} (Tsikl ${progress.cycle})`;

    // Question Text with KaTeX formatting
    this.questionText.innerHTML = this.renderMathText(question.questionText);

    // Render Geometric Diagram SVG
    this.diagramContainer.innerHTML = DiagramRenderer.render(question.diagram);

    // Render Options
    this.optionsContainer.innerHTML = '';
    shuffledOptions.forEach((opt, idx) => {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', 'false');
      btn.innerHTML = `
        <span class="option-letter">${opt.letter}</span>
        <span class="option-content">${this.renderMathText(opt.text)}</span>
      `;
      btn.addEventListener('click', () => this.selectOption(idx));
      this.optionsContainer.appendChild(btn);
    });

    // Reset feedback and action buttons
    this.feedbackContainer.innerHTML = '';
    this.feedbackContainer.style.display = 'none';
    this.btnSubmit.disabled = true;
    this.btnSubmit.style.display = 'inline-flex';
    this.btnNext.style.display = 'none';

    this.renderKaTeX();
  }

  selectOption(index) {
    if (this.quizEngine.isAnswered) return;
    this.quizEngine.selectOption(index);

    const buttons = this.optionsContainer.querySelectorAll('.option-btn');
    buttons.forEach((btn, idx) => {
      const isSelected = idx === index;
      btn.classList.toggle('selected', isSelected);
      btn.setAttribute('aria-checked', isSelected ? 'true' : 'false');
    });

    this.btnSubmit.disabled = false;
  }

  handleAnswerSubmit() {
    const result = this.quizEngine.submitAnswer();
    if (!result) return;

    const buttons = this.optionsContainer.querySelectorAll('.option-btn');
    buttons.forEach((btn, idx) => {
      btn.disabled = true;
      if (idx === result.correctOptionIndex) {
        btn.classList.add('state-correct');
      } else if (idx === result.selectedOptionIndex && !result.isCorrect) {
        btn.classList.add('state-incorrect');
      }
    });

    // Show Feedback Box
    this.feedbackContainer.style.display = 'block';
    this.feedbackContainer.className = `feedback-box ${result.isCorrect ? 'correct' : 'incorrect'}`;

    const titleHtml = result.isCorrect
      ? `<span>🎉 TO'G'RI JAVOB!</span>`
      : `<span>❌ XATO! To'g'ri javob: ${result.correctOption.letter}) ${result.correctAnswer}</span>`;

    this.feedbackContainer.innerHTML = `
      <div class="feedback-title">${titleHtml}</div>
      <div class="feedback-details">${this.renderMathText(result.explanation)}</div>
      ${result.ruleRef ? `<span class="feedback-rule-tag">📖 ${result.ruleRef}</span>` : ''}
    `;

    this.btnSubmit.style.display = 'none';
    this.btnNext.style.display = 'inline-flex';

    this.updateStats();
    this.renderKaTeX();
  }

  updateStats() {
    const stats = this.quizEngine.getStats();
    this.statAnswered.textContent = stats.totalAnswered;
    this.statCorrect.textContent = stats.correctCount;
    this.statIncorrect.textContent = stats.incorrectCount;
    this.statAccuracy.textContent = `${stats.accuracy}%`;
    this.statStreak.textContent = `🔥 ${stats.streak}`;
  }

  openFormulaModal() {
    const rule = this.formulaEngine.getRandomFormula(this.currentTopicId);
    this.renderFormulaDetails(rule);
    this.formulaModal.classList.add('open');
  }

  closeFormulaModal() {
    this.formulaModal.classList.remove('open');
  }

  renderFormulaDetails(rule) {
    if (!rule) return;

    this.formulaTitle.textContent = `${rule.number}-Qoida: ${rule.title}`;
    this.formulaCategory.textContent = rule.category;
    this.formulaDisplay.innerHTML = `\[ ${rule.formulaLatex} \]`;
    this.formulaRuleText.textContent = rule.ruleText;

    // Symbols table
    if (rule.symbols && rule.symbols.length > 0) {
      let rows = rule.symbols.map(s => `
        <tr>
          <td>\( ${s.symbol} \)</td>
          <td>${s.meaning}</td>
        </tr>
      `).join('');
      this.formulaSymbols.innerHTML = `
        <table class="formula-symbols-table">
          <thead><tr><th>Belgi</th><th>Izoh</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    } else {
      this.formulaSymbols.innerHTML = '';
    }

    this.renderKaTeX();
  }

  renderMathText(text) {
    if (!text) return '';
    return text.replace(/\$([^$]+)\$/g, (match, math) => `\( ${math} \)`);
  }

  renderKaTeX() {
    if (window.renderMathInElement) {
      window.renderMathInElement(document.body, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\[', right: '\]', display: true },
          { left: '$', right: '$', display: false },
          { left: '\(', right: '\)', display: false }
        ],
        throwOnError: false
      });
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.app = new QuizApp();
});
