export const TOPIC_2 = {
  "id": "topic-2",
  "title": "2-Mavzu: Burchaklar (Test 02)",
  "shortTitle": "2-Mavzu",
  "category": "Geometriya",
  "rulesCovered": [
    6,
    7,
    8,
    9,
    10
  ],
  "questionsCount": 16,
  "questions": [
    {
      "id": "topic2-q001",
      "number": 1,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "Chizmada $m(\\widehat{EOF}) = 20^\\circ$ bo'lsa, $m(\\widehat{DOE}) = \\alpha$ ni toping.",
      "latexGiven": "m(\\widehat{EOF}) = 20^\\circ \\implies m(\\widehat{DOE}) = \\alpha = ?",
      "options": [
        "20",
        "70",
        "120",
        "140",
        "160"
      ],
      "correctAnswer": "160",
      "diagram": {
        "type": "supplementary-line",
        "params": {
          "angle": "20\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qo'shni burchaklar xossasi",
      "explanation": "$DF$ to'g'ri chiziq ustidagi qo'shni burchaklar yig'indisi $180^\\circ$ ga teng:\n$$\\alpha + 20^\\circ = 180^\\circ \\implies \\alpha = 180^\\circ - 20^\\circ = 160^\\circ$$"
    },
    {
      "id": "topic2-q002",
      "number": 2,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$m(\\widehat{AOB}) = \\alpha$, $m(\\widehat{BOC}) = 2\\alpha - 15^\\circ$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "m(\\widehat{AOB}) = \\alpha, \\quad m(\\widehat{BOC}) = 2\\alpha - 15^\\circ \\implies \\alpha = ?",
      "options": [
        "50",
        "55",
        "60",
        "65",
        "75"
      ],
      "correctAnswer": "65",
      "diagram": {
        "type": "supplementary-expr",
        "params": {
          "expr1": "\u03b1",
          "expr2": "2\u03b1 - 15\u00b0"
        }
      },
      "ruleRef": "Qo'shni burchaklar xossasi",
      "explanation": "Qo'shni burchaklar yig'indisi $180^\\circ$ bo'ladi:\n$$\\alpha + (2\\alpha - 15^\\circ) = 180^\\circ \\implies 3\\alpha - 15^\\circ = 180^\\circ$$\n$$3\\alpha = 195^\\circ \\implies \\alpha = 65^\\circ$$"
    },
    {
      "id": "topic2-q003",
      "number": 3,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$[OA \\perp [OB$, $m(\\widehat{COB}) = 30^\\circ$ bo'lsa, $m(\\widehat{AOC}) = \\alpha$ ni toping.",
      "latexGiven": "[OA \\perp [OB, \\quad m(\\widehat{COB}) = 30^\\circ \\implies m(\\widehat{AOC}) = \\alpha = ?",
      "options": [
        "20",
        "30",
        "50",
        "60",
        "150"
      ],
      "correctAnswer": "60",
      "diagram": {
        "type": "perpendicular-split",
        "params": {
          "angle1": "30\u00b0",
          "angle2": "\u03b1",
          "labelVertex": "O"
        }
      },
      "ruleRef": "To'g'ri burchak (90\u00b0) xossasi",
      "explanation": "$OA \\perp OB$ bo'lgani uchun burchak $90^\\circ$ ga teng:\n$$\\alpha + 30^\\circ = 90^\\circ \\implies \\alpha = 60^\\circ$$"
    },
    {
      "id": "topic2-q004",
      "number": 4,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$m(\\widehat{COD}) = m(\\widehat{DOB}) = 40^\\circ$ bo'lsa, $m(\\widehat{AOC}) = \\alpha$ ni toping.",
      "latexGiven": "m(\\widehat{COD}) = m(\\widehat{DOB}) = 40^\\circ \\implies m(\\widehat{AOC}) = \\alpha = ?",
      "options": [
        "40",
        "80",
        "90",
        "100",
        "140"
      ],
      "correctAnswer": "100",
      "diagram": {
        "type": "straight-line-3-angles",
        "params": {
          "a1": "40\u00b0",
          "a2": "40\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Yoyiq burchak (180\u00b0) xossasi",
      "explanation": "$AB$ to'g'ri chiziqdagi yoyiq burchak $180^\\circ$ ga teng:\n$$\\alpha + 40^\\circ + 40^\\circ = 180^\\circ \\implies \\alpha + 80^\\circ = 180^\\circ \\implies \\alpha = 100^\\circ$$"
    },
    {
      "id": "topic2-q005",
      "number": 5,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 70^\\circ$ bo'lsa, $m(\\widehat{BCD}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 70^\\circ \\implies m(\\widehat{BCD}) = \\alpha = ?",
      "options": [
        "20",
        "30",
        "70",
        "100",
        "110"
      ],
      "correctAnswer": "70",
      "diagram": {
        "type": "z-rule-simple",
        "params": {
          "angle": "70\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 1: Z-qoidasi (Ichki almashinuvchi burchaklar)",
      "explanation": "Qoida 1 (Z-qoidasi) ga ko'ra ikki parallel to'g'ri chiziq orasidagi ichki almashinuvchi burchaklar o'zaro teng bo'ladi:\n$$\\alpha = 70^\\circ$$"
    },
    {
      "id": "topic2-q006",
      "number": 6,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{BCD}) = 40^\\circ$ bo'lsa, $m(\\widehat{ABC}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{BCD}) = 40^\\circ \\implies m(\\widehat{ABC}) = \\alpha = ?",
      "options": [
        "20",
        "40",
        "50",
        "60",
        "140"
      ],
      "correctAnswer": "40",
      "diagram": {
        "type": "z-rule-simple",
        "params": {
          "angle": "40\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 1: Z-qoidasi (Ichki almashinuvchi burchaklar)",
      "explanation": "Ichki almashinuvchi burchaklar (Z-qoidasi) o'zaro teng:\n$$\\alpha = 40^\\circ$$"
    },
    {
      "id": "topic2-q007",
      "number": 7,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{BCD}) = 80^\\circ$ bo'lsa, $m(\\widehat{CDE}) = m(\\widehat{EDF}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{BCD}) = 80^\\circ \\implies m(\\widehat{CDE}) = m(\\widehat{EDF}) = \\alpha = ?",
      "options": [
        "5",
        "10",
        "40",
        "50",
        "100"
      ],
      "correctAnswer": "40",
      "diagram": {
        "type": "z-bisector-split",
        "params": {
          "angle": "80\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 1 & Bissektrisa xossasi",
      "explanation": "$m(\\widehat{CDF}) = 80^\\circ$ (Z-qoidasi). $DE$ nuri ushbu burchakning bissektrisasi bo'lganligi sababli:\n$$2\\alpha = 80^\\circ \\implies \\alpha = 40^\\circ$$"
    },
    {
      "id": "topic2-q008",
      "number": 8,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{BCD}) = 55^\\circ$ bo'lsa, $m(\\widehat{ABC}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{BCD}) = 55^\\circ \\implies m(\\widehat{ABC}) = \\alpha = ?",
      "options": [
        "125",
        "115",
        "75",
        "60",
        "55"
      ],
      "correctAnswer": "125",
      "diagram": {
        "type": "u-rule-simple",
        "params": {
          "angle": "55\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 2: Ichki bir tomonli burchaklar (U-qoidasi)",
      "explanation": "Qoida 2 (U-qoidasi) ga binoan ichki bir tomonli burchaklar yig'indisi $180^\\circ$ ga teng:\n$$\\alpha + 55^\\circ = 180^\\circ \\implies \\alpha = 180^\\circ - 55^\\circ = 125^\\circ$$"
    },
    {
      "id": "topic2-q009",
      "number": 9,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 40^\\circ$ bo'lsa, $m(\\widehat{BCD}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 40^\\circ \\implies m(\\widehat{BCD}) = \\alpha = ?",
      "options": [
        "40",
        "50",
        "90",
        "130",
        "140"
      ],
      "correctAnswer": "140",
      "diagram": {
        "type": "u-rule-simple",
        "params": {
          "angle": "40\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 2: Ichki bir tomonli burchaklar (U-qoidasi)",
      "explanation": "Ichki bir tomonli burchaklar yig'indisi $180^\\circ$ ga teng:\n$$\\alpha + 40^\\circ = 180^\\circ \\implies \\alpha = 180^\\circ - 40^\\circ = 140^\\circ$$"
    },
    {
      "id": "topic2-q010",
      "number": 10,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 2x + 10^\\circ$, $m(\\widehat{BCD}) = 3x - 20^\\circ$ bo'lsa, $x$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 2x + 10^\\circ, \\quad m(\\widehat{BCD}) = 3x - 20^\\circ \\implies x = ?",
      "options": [
        "30",
        "34",
        "38",
        "40",
        "42"
      ],
      "correctAnswer": "38",
      "diagram": {
        "type": "u-rule-linear",
        "params": {
          "expr1": "2x + 10\u00b0",
          "expr2": "3x - 20\u00b0"
        }
      },
      "ruleRef": "Qoida 2: Ichki bir tomonli burchaklar",
      "explanation": "Ichki bir tomonli burchaklar yig'indisi $180^\\circ$ ga teng:\n$$(2x + 10^\\circ) + (3x - 20^\\circ) = 180^\\circ$$\n$$5x - 10^\\circ = 180^\\circ \\implies 5x = 190^\\circ \\implies x = 38^\\circ$$"
    },
    {
      "id": "topic2-q011",
      "number": 11,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{AOC}) = 70^\\circ$, $m(\\widehat{ABD}) = 3x - 20^\\circ$ bo'lsa, $x$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{AOC}) = 70^\\circ, \\quad m(\\widehat{ABD}) = 3x - 20^\\circ \\implies x = ?",
      "options": [
        "30",
        "70",
        "80",
        "110",
        "140"
      ],
      "correctAnswer": "30",
      "diagram": {
        "type": "corresponding-linear",
        "params": {
          "expr1": "70\u00b0",
          "expr2": "3x - 20\u00b0"
        }
      },
      "ruleRef": "Qoida 6: Mos burchaklar xossasi",
      "explanation": "Parallel to'g'ri chiziqlarda mos burchaklar o'zaro teng bo'ladi:\n$$3x - 20^\\circ = 70^\\circ \\implies 3x = 90^\\circ \\implies x = 30^\\circ$$"
    },
    {
      "id": "topic2-q012",
      "number": 12,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{AOB}) = 130^\\circ$ bo'lsa, $m(\\widehat{ACD}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{AOB}) = 130^\\circ \\implies m(\\widehat{ACD}) = \\alpha = ?",
      "options": [
        "130",
        "110",
        "100",
        "50",
        "40"
      ],
      "correctAnswer": "50",
      "diagram": {
        "type": "transversal-supplementary",
        "params": {
          "angle": "130\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 2: Ichki bir tomonli burchaklar",
      "explanation": "Ichki bir tomonli burchaklar yig'indisi $180^\\circ$ ga teng:\n$$\\alpha = 180^\\circ - 130^\\circ = 50^\\circ$$"
    },
    {
      "id": "topic2-q013",
      "number": 13,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{AOD}) = 100^\\circ$ bo'lsa, $m(\\widehat{DBC}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{AOD}) = 100^\\circ \\implies m(\\widehat{DBC}) = \\alpha = ?",
      "options": [
        "110",
        "100",
        "80",
        "70",
        "50"
      ],
      "correctAnswer": "80",
      "diagram": {
        "type": "transversal-corresponding-supp",
        "params": {
          "angle": "100\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 6 & Qo'shni burchak",
      "explanation": "Mos burchak $100^\\circ$ ga teng. Uning qo'shnisi $\\alpha$:\n$$\\alpha = 180^\\circ - 100^\\circ = 80^\\circ$$"
    },
    {
      "id": "topic2-q014",
      "number": 14,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 150^\\circ$, $m(\\widehat{BCD}) = 100^\\circ$ bo'lsa, $m(\\widehat{CDE}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 150^\\circ, \\quad m(\\widehat{BCD}) = 100^\\circ \\implies m(\\widehat{CDE}) = \\alpha = ?",
      "options": [
        "60",
        "70",
        "100",
        "110",
        "130"
      ],
      "correctAnswer": "110",
      "diagram": {
        "type": "pencil-rule-simple",
        "params": {
          "a1": "150\u00b0",
          "a2": "100\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 3: Qalam uchi qoidasi (360\u00b0)",
      "explanation": "Qoida 3 ga ko'ra uchta ichki burchak yig'indisi $360^\\circ$ ga teng:\n$$150^\\circ + 100^\\circ + \\alpha = 360^\\circ$$\n$$250^\\circ + \\alpha = 360^\\circ \\implies \\alpha = 110^\\circ$$"
    },
    {
      "id": "topic2-q015",
      "number": 15,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 2x$, $m(\\widehat{CDE}) = x + 24^\\circ$, $m(\\widehat{BCD}) = 3x$ bo'lsa, $3x$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 2x, \\quad m(\\widehat{CDE}) = x + 24^\\circ, \\quad m(\\widehat{BCD}) = 3x \\implies 3x = ?",
      "options": [
        "56",
        "60",
        "108",
        "168",
        "170"
      ],
      "correctAnswer": "168",
      "diagram": {
        "type": "pencil-rule-variable-x",
        "params": {
          "b1": "2x",
          "b2": "3x",
          "b3": "x + 24\u00b0"
        }
      },
      "ruleRef": "Qoida 3: Qalam uchi qoidasi (360\u00b0)",
      "explanation": "Uchta ichki burchak yig'indisi $360^\\circ$ bo'ladi:\n$$2x + 3x + (x + 24^\\circ) = 360^\\circ$$\n$$6x + 24^\\circ = 360^\\circ \\implies 6x = 336^\\circ \\implies x = 56^\\circ$$\nBizdan $m(\\widehat{BCD}) = 3x$ so'ralgan:\n$$3x = 3 \\cdot 56^\\circ = 168^\\circ$$"
    },
    {
      "id": "topic2-q016",
      "number": 16,
      "topicId": "topic-2",
      "topicTitle": "2-Mavzu: Burchaklar \u2014 Test 02",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 135^\\circ$, $m(\\widehat{CDE}) = 75^\\circ$ bo'lsa, $m(\\widehat{BCD}) = \\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 135^\\circ, \\quad m(\\widehat{CDE}) = 75^\\circ \\implies m(\\widehat{BCD}) = \\alpha = ?",
      "options": [
        "75",
        "80",
        "105",
        "120",
        "135"
      ],
      "correctAnswer": "120",
      "diagram": {
        "type": "m-rule-zigzag",
        "params": {
          "a1": "135\u00b0",
          "a2": "75\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 7: M-qoidasi (Zig-zag burchaklar)",
      "explanation": "Qoida 7 ga binoan chapga qaragan o'tkir burchak $180^\\circ - 135^\\circ = 45^\\circ$.\nO'ng tomonga qaragan burchak $\\alpha$:\n$$\\alpha = 45^\\circ + 75^\\circ = 120^\\circ$$"
    }
  ]
};
