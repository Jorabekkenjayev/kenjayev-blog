import { TOPIC_1 } from './topic1.js';
import { TOPIC_2 } from './topic2.js';

export const TOPICS = [
  TOPIC_1,
  TOPIC_2
];

export function getTopicById(id) {
  return TOPICS.find(t => t.id === id) || TOPIC_1;
}

export function getAllQuestions() {
  return TOPICS.flatMap(t => t.questions);
}
