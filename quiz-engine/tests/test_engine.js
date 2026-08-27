import { TOPIC_1 } from '../js/data/topic1.js';
import { TOPIC_2 } from '../js/data/topic2.js';
import { ALL_RULES } from '../js/data/all_rules.js';
import { TOPICS, getAllQuestions } from '../js/data/topics.js';
import { QuizEngine } from '../js/engines/quizEngine.js';
import { FormulaEngine } from '../js/engines/formulaEngine.js';

let totalTests = 0;
let passedTests = 0;

function assert(condition, message) {
  totalTests++;
  if (!condition) {
    console.error(`❌ FAIL: ${message}`);
    process.exit(1);
  } else {
    passedTests++;
  }
}

console.log("=== PUZA GEOMETRI ENGINE VALIDATION SUITE ===");

// 1. Validate Rules
assert(ALL_RULES.length === 10, `All 10 fundamental rules exist (found ${ALL_RULES.length})`);
ALL_RULES.forEach(rule => {
  assert(rule.id && rule.title && rule.formulaLatex && rule.ruleText, `Rule #${rule.number} has valid structure`);
  assert(Array.isArray(rule.symbols) && rule.symbols.length > 0, `Rule #${rule.number} has symbol descriptions`);
});

// 2. Validate Topic 1 Questions
assert(TOPIC_1.questions.length === 16, `Topic 1 has exactly 16 questions (found ${TOPIC_1.questions.length})`);
TOPIC_1.questions.forEach(q => {
  assert(q.id && q.questionText && q.correctAnswer && q.explanation, `Topic 1 Question #${q.number} is complete`);
  assert(Array.isArray(q.options) && q.options.length >= 4, `Topic 1 Question #${q.number} has >= 4 options`);
  assert(q.options.includes(q.correctAnswer), `Topic 1 Question #${q.number} correctAnswer '${q.correctAnswer}' is in options`);
});

// 3. Validate Topic 2 Questions
assert(TOPIC_2.questions.length === 16, `Topic 2 has exactly 16 questions (found ${TOPIC_2.questions.length})`);
TOPIC_2.questions.forEach(q => {
  assert(q.id && q.questionText && q.correctAnswer && q.explanation, `Topic 2 Question #${q.number} is complete`);
  assert(Array.isArray(q.options) && q.options.length >= 4, `Topic 2 Question #${q.number} has >= 4 options`);
  assert(q.options.includes(q.correctAnswer), `Topic 2 Question #${q.number} correctAnswer '${q.correctAnswer}' is in options`);
});

// 4. Validate All Questions in Registry
const allQuestions = getAllQuestions();
assert(allQuestions.length === 32, `Total registered questions is 32 (found ${allQuestions.length})`);

// 5. Test QuizEngine Randomization & Non-repeating Cycles
const quiz = new QuizEngine();
quiz.setTopic('topic-1');
const seenIds = new Set();
for (let i = 0; i < 16; i++) {
  const data = quiz.nextQuestion();
  assert(data && data.question, `Quiz generated question #${i + 1}`);
  assert(!seenIds.has(data.question.id), `Question ${data.question.id} is unique within cycle`);
  seenIds.add(data.question.id);
  assert(data.shuffledOptions.length === 5, `Options shuffled correctly`);
  assert(data.shuffledOptions.some(o => o.isCorrect), `One option is marked correct`);
}

// 6. Test Answer Verification
quiz.selectOption(0);
const submitResult = quiz.submitAnswer();
assert(submitResult !== null, `Submit answer returns evaluation object`);
assert(typeof submitResult.isCorrect === 'boolean', `isCorrect is boolean`);
assert(submitResult.explanation.length > 0, `Explanation is provided`);
assert(quiz.getStats().totalAnswered === 1, `Total answered recorded accurately in stats`);

// 7. Test Formula Engine
const formulaEngine = new FormulaEngine();
const randomRule = formulaEngine.getRandomFormula('topic-1');
assert(randomRule !== null && randomRule.formulaLatex, `Random formula selected`);
const nextRule = formulaEngine.getNextFormula('topic-1');
assert(nextRule !== null, `Sequential next formula navigation works`);

console.log(`\n========================================`);
console.log(`🎉 ALL ${passedTests}/${totalTests} TESTS PASSED WITH ZERO ERRORS!`);
console.log(`========================================`);
