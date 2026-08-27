import { ALL_RULES } from '../data/all_rules.js';

export class FormulaEngine {
  constructor() {
    this.rules = [...ALL_RULES];
    this.currentIndex = 0;
    this.history = [];
  }

  /**
   * Get all rules or filter by topic
   */
  getRules(topicId = null) {
    if (!topicId || topicId === 'all') {
      return this.rules;
    }
    return this.rules.filter(r => r.topicId === topicId);
  }

  /**
   * Pick random formula without immediately repeating previous one
   */
  getRandomFormula(topicId = null) {
    const filtered = this.getRules(topicId);
    if (filtered.length === 0) return null;
    if (filtered.length === 1) {
      this.currentIndex = this.rules.indexOf(filtered[0]);
      return filtered[0];
    }

    let nextIndex;
    let attempts = 0;
    do {
      nextIndex = Math.floor(Math.random() * filtered.length);
      attempts++;
    } while (filtered[nextIndex] === this.rules[this.currentIndex] && attempts < 10);

    const chosenRule = filtered[nextIndex];
    this.currentIndex = this.rules.indexOf(chosenRule);
    this.history.push(this.currentIndex);
    return chosenRule;
  }

  /**
   * Get next formula sequentially
   */
  getNextFormula(topicId = null) {
    const filtered = this.getRules(topicId);
    if (filtered.length === 0) return null;

    const currentInFiltered = filtered.indexOf(this.rules[this.currentIndex]);
    const nextInFiltered = (currentInFiltered + 1) % filtered.length;
    const chosenRule = filtered[nextInFiltered];
    this.currentIndex = this.rules.indexOf(chosenRule);
    return chosenRule;
  }

  /**
   * Get previous formula
   */
  getPrevFormula(topicId = null) {
    const filtered = this.getRules(topicId);
    if (filtered.length === 0) return null;

    const currentInFiltered = filtered.indexOf(this.rules[this.currentIndex]);
    const prevInFiltered = (currentInFiltered - 1 + filtered.length) % filtered.length;
    const chosenRule = filtered[prevInFiltered];
    this.currentIndex = this.rules.indexOf(chosenRule);
    return chosenRule;
  }

  getFormulaById(id) {
    return this.rules.find(r => r.id === id) || this.rules[0];
  }
}
