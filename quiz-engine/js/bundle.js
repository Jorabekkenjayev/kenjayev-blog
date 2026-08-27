/**
 * Standalone Bundled Script for Puza Geometri Engine
 * Supports both file:// protocol direct double-click and http:// web servers.
 */
(function() {
  'use strict';

/**
 * Puza Geometri - Burchaklar: 10 Fundamental Qoidalar va Formulalar Bazasi
 */
const ALL_RULES = [
  {
    id: "qoida-1",
    number: 1,
    title: "Ichki almashinuvchi burchaklar (Z-qoidasi)",
    formulaLatex: "d_1 \\parallel d_2 \\implies \\alpha = \\alpha",
    category: "Parallel to'g'ri chiziqlar",
    topicId: "topic-1",
    topicName: "1-Mavzu: Burchaklar (Test 01)",
    symbols: [
      { symbol: "d_1, d_2", meaning: "O'zaro parallel to'g'ri chiziqlar" },
      { symbol: "\\alpha", meaning: "Ichki almashinuvchi teng burchaklar" }
    ],
    ruleText: "Ikki parallel to'g'ri chiziqni uchinchi to'g'ri chiziq (kesuvchi) kesib o'tganda hosil bo'lgan ichki almashinuvchi burchaklar o'zaro teng bo'ladi (Z shakli).",
    diagramType: "z-rule",
    examples: [
      { given: "40^\\circ", target: "\\alpha", answer: "40^\\circ" },
      { given: "x + 40^\\circ = 2x + 10^\\circ", target: "x", answer: "30^\\circ" }
    ]
  },
  {
    id: "qoida-2",
    number: 2,
    title: "Ichki bir tomonli burchaklar (U / C-qoidasi)",
    formulaLatex: "d_1 \\parallel d_2 \\implies \\alpha + \\beta = 180^\\circ",
    category: "Parallel to'g'ri chiziqlar",
    topicId: "topic-1",
    topicName: "1-Mavzu: Burchaklar (Test 01)",
    symbols: [
      { symbol: "d_1, d_2", meaning: "O'zaro parallel to'g'ri chiziqlar" },
      { symbol: "\\alpha, \\beta", meaning: "Parallel chiziqlar orasidagi ichki bir tomonli burchaklar" }
    ],
    ruleText: "Ikki parallel to'g'ri chiziq orasidagi ichki bir tomonli burchaklar yig'indisi har doim 180° ga teng bo'ladi (U yoki C shakli).",
    diagramType: "u-rule",
    examples: [
      { given: "70^\\circ", target: "\\alpha", answer: "110^\\circ" }
    ]
  },
  {
    id: "qoida-3",
    number: 3,
    title: "Qalam uchi qoidasi (3 ta ichki burchak)",
    formulaLatex: "d_1 \\parallel d_2 \\implies a + b + c = 360^\\circ",
    category: "Siniq chiziq burchaklari",
    topicId: "topic-1",
    topicName: "1-Mavzu: Burchaklar (Test 01)",
    symbols: [
      { symbol: "d_1, d_2", meaning: "Parallel to'g'ri chiziqlar" },
      { symbol: "a, b, c", meaning: "Siniq chiziq hosil qilgan 3 ta ichki bir tomonli burchak" }
    ],
    ruleText: "Ikki parallel to'g'ri chiziq orasida bitta uchi bo'lgan siniq chiziq hosil qilgan uchta ichki burchakning yig'indisi 360° ga teng.",
    diagramType: "pencil-rule-3",
    examples: [
      { given: "140^\\circ, 100^\\circ", target: "\\alpha", answer: "120^\\circ" }
    ]
  },
  {
    id: "qoida-4",
    number: 4,
    title: "Ko'p burchakli qalam uchi qoidasi",
    formulaLatex: "d_1 \\parallel d_2 \\implies a + b + c + d = 540^\\circ \\quad \\left(\\sum = (n-1) \\cdot 180^\\circ\\right)",
    category: "Siniq chiziq burchaklari",
    topicId: "topic-1",
    topicName: "1-Mavzu: Burchaklar (Test 01)",
    symbols: [
      { symbol: "n", meaning: "Ichki burchaklar soni" },
      { symbol: "a, b, c, d", meaning: "Ketma-ket bir tomonli ichki burchaklar" }
    ],
    ruleText: "Parallel to'g'ri chiziqlar orasidagi n ta bir tomonli burchaklar yig'indisi (n - 1) * 180° ga teng (4 ta burchak uchun: 3 * 180° = 540°).",
    diagramType: "pencil-rule-4"
  },
  {
    id: "qoida-5",
    number: 5,
    title: "Yordamchi parallel to'g'ri chiziq o'tkazish",
    formulaLatex: "d_1 \\parallel d_2 \\parallel d_3",
    category: "Geometrik yasash usullari",
    topicId: "topic-1",
    topicName: "1-Mavzu: Burchaklar (Test 01)",
    symbols: [
      { symbol: "d_3", meaning: "Burchak uchi orqali o'tkazilgan yordamchi parallel chiziq" }
    ],
    ruleText: "Murakkab siniq chiziqli burchak masalalarida burchak uchi orqali berilgan chiziqlarga parallel yordamchi chiziq o'tkazilib, masala sodda Z va U qoidalariga ajratiladi.",
    diagramType: "auxiliary-line"
  },
  {
    id: "qoida-6",
    number: 6,
    title: "Mos burchaklar va parallel to'g'ri chiziqlar to'plami",
    formulaLatex: "d_1 \\parallel d_2 \\land d_3 \\parallel d_4 \\implies \\alpha = \\alpha",
    category: "Parallel to'g'ri chiziqlar",
    topicId: "topic-2",
    topicName: "2-Mavzu: Burchaklar (Test 02)",
    symbols: [
      { symbol: "d_1 \\parallel d_2, d_3 \\parallel d_4", meaning: "O'zaro parallel to'g'ri chiziqlar juftligi" },
      { symbol: "\\alpha", meaning: "Tomonlari parallel bo'lgan bir xil turdagi burchaklar" }
    ],
    ruleText: "Tomonlari o'zaro parallel bo'lgan bir xil turdagi (ikkalasi ham o'tkir yoki ikkalasi ham o'tmas) burchaklar o'zaro teng bo'ladi.",
    diagramType: "corresponding-angles"
  },
  {
    id: "qoida-7",
    number: 7,
    title: "M-qoidasi (Zig-zag burchaklar)",
    formulaLatex: "d_1 \\parallel d_2 \\implies \\alpha = a + b",
    category: "Zig-zag qoidalari",
    topicId: "topic-2",
    topicName: "2-Mavzu: Burchaklar (Test 02)",
    symbols: [
      { symbol: "\\alpha", meaning: "O'ng tomonga qaragan burchak" },
      { symbol: "a, b", meaning: "Chap tomonga qaragan burchaklar" }
    ],
    ruleText: "Parallel to'g'ri chiziqlar orasidagi bitta siniqqa ega bo'lgan M-shaklidagi burchakda o'ngga qaragan burchak chapga qaragan burchaklar yig'indisiga teng: α = a + b.",
    diagramType: "m-rule"
  },
  {
    id: "qoida-8",
    number: 8,
    title: "Ko'p bo'g'inli Zig-zag qoidasi",
    formulaLatex: "d_1 \\parallel d_2 \\implies a + b + c = x + y",
    category: "Zig-zag qoidalari",
    topicId: "topic-2",
    topicName: "2-Mavzu: Burchaklar (Test 02)",
    symbols: [
      { symbol: "a, b, c", meaning: "Chap tomonga yo'nalgan burchaklar" },
      { symbol: "x, y", meaning: "O'ng tomonga yo'nalgan burchaklar" }
    ],
    ruleText: "Parallel to'g'ri chiziqlar orasida navbatma-navbat yo'nalgan burchaklarda chapga qaragan burchaklar yig'indisi o'ngga qaragan burchaklar yig'indisiga teng.",
    diagramType: "multi-zigzag"
  },
  {
    id: "qoida-9",
    number: 9,
    title: "Burchak bissektrisalari orasidagi burchak",
    formulaLatex: "x = \\frac{a + b}{2}",
    category: "Bissektrisa qoidalari",
    topicId: "topic-2",
    topicName: "2-Mavzu: Burchaklar (Test 02)",
    symbols: [
      { symbol: "a, b", meaning: "Asosiy burchaklar" },
      { symbol: "x", meaning: "Bissektrisalar hosil qilgan o'rta burchak" }
    ],
    ruleText: "Burchaklar bissektrisalari orasidagi burchak ushbu burchaklarning arifmetik o'rtachasiga teng bo'ladi.",
    diagramType: "bisector-angle"
  },
  {
    id: "qoida-10",
    number: 10,
    title: "Qo'shni burchaklar bissektrisalari",
    formulaLatex: "2a + 2b = 180^\\circ \\implies a + b = 90^\\circ",
    category: "Bissektrisa qoidalari",
    topicId: "topic-2",
    topicName: "2-Mavzu: Burchaklar (Test 02)",
    symbols: [
      { symbol: "2a, 2b", meaning: "Qo'shni burchaklar (yig'indisi 180°)" },
      { symbol: "a + b", meaning: "Bissektrisalar orasidagi burchak (90°)" }
    ],
    ruleText: "Yoyiq burchak hosil qiluvchi ikkita qo'shni burchakning bissektrisalari orasidagi burchak har doim 90° (to'g'ri burchak) ga teng bo'ladi.",
    diagramType: "adjacent-bisectors"
  }
];


const TOPIC_1 = {
  "id": "topic-1",
  "title": "1-Mavzu: Burchaklar (Test 01)",
  "shortTitle": "1-Mavzu",
  "category": "Geometriya",
  "rulesCovered": [
    1,
    2,
    3,
    4,
    5
  ],
  "questionsCount": 16,
  "questions": [
    {
      "id": "topic1-q001",
      "number": 1,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "Quyidagi chizmada $AE \\perp [BC$, $m(\\widehat{EBD}) = 44^\\circ$, $m(\\widehat{CBD}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "AE \\perp [BC, \\quad m(\\widehat{EBD}) = 44^\\circ, \\quad m(\\widehat{CBD}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "20",
        "22",
        "24",
        "36",
        "46"
      ],
      "correctAnswer": "46",
      "diagram": {
        "type": "perpendicular-split",
        "params": {
          "angle1": "44\u00b0",
          "angle2": "\u03b1",
          "labelVertex": "B",
          "ray1": "E",
          "ray2": "D",
          "ray3": "C"
        }
      },
      "ruleRef": "Qo'shni va to'g'ri burchak xossasi",
      "explanation": "Berilishiga ko'ra $AE \\perp [BC$, demak $m(\\widehat{EBC}) = 90^\\circ$. $BD$ nuri to'g'ri burchakni ikkiga ajratadi:\n$$m(\\widehat{EBD}) + m(\\widehat{CBD}) = 90^\\circ \\implies 44^\\circ + \\alpha = 90^\\circ$$\n$$\\alpha = 90^\\circ - 44^\\circ = 46^\\circ$$"
    },
    {
      "id": "topic1-q002",
      "number": 2,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$AC \\perp [BH$, $m(\\widehat{CBD}) = m(\\widehat{HBG})$, $m(\\widehat{GBF}) = m(\\widehat{FBE})$, $m(\\widehat{EBD}) = 30^\\circ$ bo'lsa, $m(\\widehat{CBF})$ ni toping.",
      "latexGiven": "AC \\perp [BH, \\quad m(\\widehat{CBD}) = m(\\widehat{HBG}) = x, \\quad m(\\widehat{GBF}) = m(\\widehat{FBE}) = y, \\quad m(\\widehat{EBD}) = 30^\\circ \\implies m(\\widehat{CBF}) = ?",
      "options": [
        "15",
        "30",
        "45",
        "60",
        "75"
      ],
      "correctAnswer": "60",
      "diagram": {
        "type": "multi-bisector-perpendicular",
        "params": {
          "givenAngle": "30\u00b0",
          "rightAngle": "90\u00b0"
        }
      },
      "ruleRef": "Qoida 10: Bissektrisalar va to'g'ri burchak",
      "explanation": "$AC \\perp BH \\implies m(\\widehat{CBH}) = 90^\\circ$.\n$m(\\widehat{CBD}) = m(\\widehat{HBG}) = x$ va $m(\\widehat{GBF}) = m(\\widehat{FBE}) = y$ deb olsak:\n$$2x + 2y + 30^\\circ = 90^\\circ \\implies 2(x+y) = 60^\\circ \\implies x+y = 30^\\circ$$\n$$m(\\widehat{CBF}) = x + 30^\\circ + y = (x+y) + 30^\\circ = 30^\\circ + 30^\\circ = 60^\\circ$$"
    },
    {
      "id": "topic1-q003",
      "number": 3,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "Chizmada $m(\\widehat{AOB}) = 270^\\circ - 2x$, $m(\\widehat{BOC}) = 2x - 10^\\circ$ bo'lsa, $m(\\widehat{AOC})$ burchakni toping.",
      "latexGiven": "m(\\widehat{AOB}) = 270^\\circ - 2x, \\quad m(\\widehat{BOC}) = 2x - 10^\\circ \\implies m(\\widehat{AOC}) = ?",
      "options": [
        "90",
        "100",
        "110",
        "120",
        "130"
      ],
      "correctAnswer": "100",
      "diagram": {
        "type": "complete-angle-360",
        "params": {
          "expr1": "270 - 2x",
          "expr2": "2x - 10"
        }
      },
      "ruleRef": "To'liq burchak (360\u00b0) xossasi",
      "explanation": "Bir nuqta atrofidagi barcha burchaklar yig'indisi $360^\\circ$ ga teng:\n$$m(\\widehat{AOB}) + m(\\widehat{BOC}) + m(\\widehat{AOC}) = 360^\\circ$$\n$$(270^\\circ - 2x) + (2x - 10^\\circ) + m(\\widehat{AOC}) = 360^\\circ$$\n$$260^\\circ + m(\\widehat{AOC}) = 360^\\circ \\implies m(\\widehat{AOC}) = 100^\\circ$$"
    },
    {
      "id": "topic1-q004",
      "number": 4,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $d_3 \\parallel d_4$, $m(\\widehat{DBC}) = 20^\\circ$, $m(\\widehat{ECF}) = 40^\\circ$ bo'lsa, $m(\\widehat{ABC})$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad d_3 \\parallel d_4, \\quad m(\\widehat{DBC}) = 20^\\circ, \\quad m(\\widehat{ECF}) = 40^\\circ \\implies m(\\widehat{ABC}) = ?",
      "options": [
        "30",
        "40",
        "60",
        "70",
        "80"
      ],
      "correctAnswer": "60",
      "diagram": {
        "type": "parallel-grid-angles",
        "params": {
          "angle1": "20\u00b0",
          "angle2": "40\u00b0"
        }
      },
      "ruleRef": "Qoida 6: Mos burchaklar xossasi",
      "explanation": "$d_1 \\parallel d_2$ va $d_3 \\parallel d_4$ bo'lganligi sababli, mos burchaklar teng: $m(\\widehat{ABD}) = m(\\widehat{ECF}) = 40^\\circ$.\n$$m(\\widehat{ABC}) = m(\\widehat{ABD}) + m(\\widehat{DBC}) = 40^\\circ + 20^\\circ = 60^\\circ$$"
    },
    {
      "id": "topic1-q005",
      "number": 5,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_4$, $d_2 \\parallel d_3$, $m(\\widehat{GEF}) = x - 55^\\circ$, $m(\\widehat{ABC}) = 2x + 10^\\circ$ bo'lsa, $x$ ni toping.",
      "latexGiven": "d_1 \\parallel d_4, \\quad d_2 \\parallel d_3, \\quad m(\\widehat{GEF}) = x - 55^\\circ, \\quad m(\\widehat{ABC}) = 2x + 10^\\circ \\implies x = ?",
      "options": [
        "15",
        "45",
        "60",
        "75",
        "85"
      ],
      "correctAnswer": "75",
      "diagram": {
        "type": "crossed-parallel-angles",
        "params": {
          "expr1": "x - 55\u00b0",
          "expr2": "2x + 10\u00b0"
        }
      },
      "ruleRef": "Qoida 2: Ichki bir tomonli burchaklar (U-qoidasi)",
      "explanation": "Tomonlari parallel bo'lgan burchaklar ichki bir tomonli bo'lib, ularning yig'indisi $180^\\circ$ ga teng:\n$$(x - 55^\\circ) + (2x + 10^\\circ) = 180^\\circ \\implies 3x - 45^\\circ = 180^\\circ$$\n$$3x = 225^\\circ \\implies x = 75^\\circ$$"
    },
    {
      "id": "topic1-q006",
      "number": 6,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 110^\\circ$, $m(\\widehat{BCD}) = 20^\\circ$, $m(\\widehat{EDC}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 110^\\circ, \\quad m(\\widehat{BCD}) = 20^\\circ, \\quad m(\\widehat{EDC}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "50",
        "70",
        "80",
        "110",
        "130"
      ],
      "correctAnswer": "130",
      "diagram": {
        "type": "zigzag-opposite-rays",
        "params": {
          "angle1": "110\u00b0",
          "angle2": "20\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 5 & Qoida 1: Yordamchi chiziq va Z-qoidasi",
      "explanation": "$C$ nuqtasi orqali $d_1$ va $d_2$ ga parallel to'g'ri chiziq o'tkazamiz. Yuqori burchak ichki almashinuvchi bo'lib $180^\\circ - 110^\\circ = 70^\\circ$ yoki to'g'ridan-to'g'ri $d_1$ ga parallel yo'nalishda $110^\\circ + 20^\\circ = 130^\\circ$ hosil bo'ladi. Demak, $\\alpha = 130^\\circ$."
    },
    {
      "id": "topic1-q007",
      "number": 7,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 70^\\circ$, $m(\\widehat{EDC}) = 80^\\circ$, $m(\\widehat{BCD}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 70^\\circ, \\quad m(\\widehat{EDC}) = 80^\\circ, \\quad m(\\widehat{BCD}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "30",
        "40",
        "45",
        "50",
        "55"
      ],
      "correctAnswer": "30",
      "diagram": {
        "type": "triangle-parallel-cut",
        "params": {
          "angle1": "70\u00b0",
          "angle2": "80\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 1: Parallel to'g'ri chiziqlar va uchburchak burchaklari",
      "explanation": "$d_1 \\parallel d_2$ bo'lgani uchun $m(\\widehat{DEC}) = m(\\widehat{ABC}) = 70^\\circ$ (mos burchak) yoki ichki burchak $180^\\circ - 80^\\circ = 100^\\circ$.\n$\\triangle CDE$ uchburchakda burchaklar yig'indisi $180^\\circ$:\n$$70^\\circ + 80^\\circ + \\alpha = 180^\\circ \\implies \\alpha = 180^\\circ - 150^\\circ = 30^\\circ$$"
    },
    {
      "id": "topic1-q008",
      "number": 8,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{BCD}) = 15^\\circ$, $m(\\widehat{EDC}) = 65^\\circ$, $m(\\widehat{ABC}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{BCD}) = 15^\\circ, \\quad m(\\widehat{EDC}) = 65^\\circ, \\quad m(\\widehat{ABC}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "70",
        "80",
        "100",
        "110",
        "120"
      ],
      "correctAnswer": "80",
      "diagram": {
        "type": "triangle-exterior-angle",
        "params": {
          "angle1": "15\u00b0",
          "angle2": "65\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 1: Uchburchak tashqi burchagi xossasi",
      "explanation": "$d_1 \\parallel d_2$ bo'lgani uchun mos burchak $65^\\circ$ ko'chadi. Uchburchakning tashqi burchagi o'ziga qo'shni bo'lmagan ikki ichki burchak yig'indisiga teng:\n$$\\alpha = 65^\\circ + 15^\\circ = 80^\\circ$$"
    },
    {
      "id": "topic1-q009",
      "number": 9,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{BCD}) = 175^\\circ$, $m(\\widehat{GBC}) = 70^\\circ$, $m(\\widehat{CDF}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{BCD}) = 175^\\circ, \\quad m(\\widehat{GBC}) = 70^\\circ, \\quad m(\\widehat{CDF}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "85",
        "95",
        "100",
        "104",
        "105"
      ],
      "correctAnswer": "105",
      "diagram": {
        "type": "pencil-head-exterior",
        "params": {
          "extAngle": "70\u00b0",
          "midAngle": "175\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 3: Qalam uchi qoidasi (360\u00b0)",
      "explanation": "Ichki burchak: $m(\\widehat{ABC}) = 180^\\circ - 70^\\circ = 110^\\circ$.\nQalam uchi qoidasiga ko'ra 3 ta ichki burchak yig'indisi $360^\\circ$:\n$$110^\\circ + 175^\\circ + m(\\widehat{CDE}) = 360^\\circ \\implies 285^\\circ + m(\\widehat{CDE}) = 360^\\circ \\implies m(\\widehat{CDE}) = 75^\\circ$$\nQo'shni burchak orqali $\\alpha$ ni topamiz:\n$$\\alpha = 180^\\circ - 75^\\circ = 105^\\circ$$"
    },
    {
      "id": "topic1-q010",
      "number": 10,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 110^\\circ$, $m(\\widehat{BCD}) = 70^\\circ$, $m(\\widehat{DEF}) = 60^\\circ$, $m(\\widehat{EFG}) = 140^\\circ$, $m(\\widehat{CDE}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 110^\\circ, \\quad m(\\widehat{BCD}) = 70^\\circ, \\quad m(\\widehat{DEF}) = 60^\\circ, \\quad m(\\widehat{EFG}) = 140^\\circ, \\quad m(\\widehat{CDE}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "10",
        "20",
        "30",
        "40",
        "50"
      ],
      "correctAnswer": "20",
      "diagram": {
        "type": "multi-zigzag-step",
        "params": {
          "a1": "110\u00b0",
          "a2": "70\u00b0",
          "a3": "\u03b1",
          "a4": "60\u00b0",
          "a5": "140\u00b0"
        }
      },
      "ruleRef": "Qoida 8: Ko'p bo'g'inli Zig-zag qoidasi",
      "explanation": "Chapga va o'ngga qaragan o'tkir burchaklarni ajratamiz:\nChapga qaraganlar: $(180^\\circ - 110^\\circ) + \\alpha + (180^\\circ - 140^\\circ) = 70^\\circ + \\alpha + 40^\\circ = 110^\\circ + \\alpha$\nO'ngga qaraganlar: $70^\\circ + 60^\\circ = 130^\\circ$\n$$110^\\circ + \\alpha = 130^\\circ \\implies \\alpha = 20^\\circ$$"
    },
    {
      "id": "topic1-q011",
      "number": 11,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 10x$, $m(\\widehat{BCD}) = 12x$, $m(\\widehat{CDE}) = 14x$ bo'lsa, $m(\\widehat{CDE})$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 10x, \\quad m(\\widehat{BCD}) = 12x, \\quad m(\\widehat{CDE}) = 14x \\implies m(\\widehat{CDE}) = ?",
      "options": [
        "30",
        "70",
        "80",
        "110",
        "140"
      ],
      "correctAnswer": "140",
      "diagram": {
        "type": "pencil-rule-variables",
        "params": {
          "b1": "10x",
          "b2": "12x",
          "b3": "14x"
        }
      },
      "ruleRef": "Qoida 3: Qalam uchi qoidasi (360\u00b0)",
      "explanation": "Qoida 3 ga binoan parallel chiziqlar orasidagi 3 ta burchak yig'indisi $360^\\circ$ ga teng:\n$$10x + 12x + 14x = 360^\\circ \\implies 36x = 360^\\circ \\implies x = 10^\\circ$$\nBizdan $m(\\widehat{CDE}) = 14x$ ni topish so'ralgan:\n$$m(\\widehat{CDE}) = 14 \\cdot 10^\\circ = 140^\\circ$$"
    },
    {
      "id": "topic1-q012",
      "number": 12,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2 \\parallel d_3$, $m(\\widehat{ABC}) = 100^\\circ$, $m(\\widehat{CDE}) = 110^\\circ$, $m(\\widehat{BCD}) = m(\\widehat{DCF})$, $m(\\widehat{CFG}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2 \\parallel d_3, \\quad m(\\widehat{ABC}) = 100^\\circ, \\quad m(\\widehat{CDE}) = 110^\\circ, \\quad m(\\widehat{BCD}) = m(\\widehat{DCF}), \\quad m(\\widehat{CFG}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "110",
        "120",
        "130",
        "140",
        "150"
      ],
      "correctAnswer": "150",
      "diagram": {
        "type": "triple-parallel-bisector",
        "params": {
          "a1": "100\u00b0",
          "a2": "110\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 2 & 5: Parallel chiziqlar va bissektrisa",
      "explanation": "$C$ nuqtasi orqali parallel chiziqlar kesilganda $m(\\widehat{BCD}) = 30^\\circ$ topiladi. Bissektrisa bo'lgani uchun $m(\\widehat{DCF}) = 30^\\circ$. So'ngra $d_2 \\parallel d_3$ orasidagi ichki bir tomonli burchak:\n$$\\alpha = 180^\\circ - 30^\\circ = 150^\\circ$$"
    },
    {
      "id": "topic1-q013",
      "number": 13,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 50^\\circ$, $m(\\widehat{GEF}) = 110^\\circ$, $m(\\widehat{GDA}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 50^\\circ, \\quad m(\\widehat{GEF}) = 110^\\circ, \\quad m(\\widehat{GDA}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "20",
        "30",
        "40",
        "50",
        "60"
      ],
      "correctAnswer": "40",
      "diagram": {
        "type": "parallel-triangle-intersection",
        "params": {
          "a1": "50\u00b0",
          "a2": "110\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 1 & 6: Mos burchaklar va uchburchak",
      "explanation": "Mos burchaklar va uchburchak burchaklari yig'indisi orqali:\n$$m(\\widehat{DGE}) = 180^\\circ - 110^\\circ = 70^\\circ$$\n$$\\alpha = 180^\\circ - (50^\\circ + 90^\\circ) = 40^\\circ \\quad \\text{yoki} \\quad \\alpha = 110^\\circ - 50^\\circ - 20^\\circ = 40^\\circ$$"
    },
    {
      "id": "topic1-q014",
      "number": 14,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABF}) = m(\\widehat{FBC})$, $m(\\widehat{FDE}) = m(\\widehat{CDF})$, $m(\\widehat{BFD}) = 150^\\circ$, $m(\\widehat{BCD}) = \\alpha$ bo'lsa, $\\alpha$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABF}) = m(\\widehat{FBC}), \\quad m(\\widehat{FDE}) = m(\\widehat{CDF}), \\quad m(\\widehat{BFD}) = 150^\\circ, \\quad m(\\widehat{BCD}) = \\alpha \\implies \\alpha = ?",
      "options": [
        "60",
        "70",
        "100",
        "110",
        "130"
      ],
      "correctAnswer": "100",
      "diagram": {
        "type": "parallel-double-bisector",
        "params": {
          "midAngle": "150\u00b0",
          "target": "\u03b1"
        }
      },
      "ruleRef": "Qoida 9: Bissektrisalar orasidagi burchak",
      "explanation": "Parallel to'g'ri chiziqlarda bissektrisalar orasidagi burchak formulasiga ko'ra:\n$$m(\\widehat{BFD}) = 180^\\circ - \\frac{180^\\circ - \\alpha}{2} \\implies 150^\\circ = 90^\\circ + \\frac{\\alpha}{2} \\dots \\implies \\alpha = 100^\\circ$$"
    },
    {
      "id": "topic1-q015",
      "number": 15,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ABC}) = 140^\\circ + x$, $m(\\widehat{BCD}) = 3x$ bo'lsa, $x$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ABC}) = 140^\\circ + x, \\quad m(\\widehat{BCD}) = 3x \\implies x = ?",
      "options": [
        "5",
        "10",
        "11",
        "12",
        "13"
      ],
      "correctAnswer": "10",
      "diagram": {
        "type": "u-rule-linear",
        "params": {
          "expr1": "140\u00b0 + x",
          "expr2": "3x"
        }
      },
      "ruleRef": "Qoida 2: Ichki bir tomonli burchaklar (U-qoidasi)",
      "explanation": "Qoida 2 ga binoan ichki bir tomonli burchaklar yig'indisi $180^\\circ$ ga teng:\n$$(140^\\circ + x) + 3x = 180^\\circ$$\n$$140^\\circ + 4x = 180^\\circ \\implies 4x = 40^\\circ \\implies x = 10^\\circ$$"
    },
    {
      "id": "topic1-q016",
      "number": 16,
      "topicId": "topic-1",
      "topicTitle": "1-Mavzu: Burchaklar \u2014 Test 01",
      "questionText": "$d_1 \\parallel d_2$, $m(\\widehat{ACD}) = 80^\\circ$, $m(\\widehat{CDB}) = m(\\widehat{BDE})$ bo'lsa, $m(\\widehat{ABD})$ ni toping.",
      "latexGiven": "d_1 \\parallel d_2, \\quad m(\\widehat{ACD}) = 80^\\circ, \\quad m(\\widehat{CDB}) = m(\\widehat{BDE}) \\implies m(\\widehat{ABD}) = ?",
      "options": [
        "50",
        "70",
        "100",
        "130",
        "150"
      ],
      "correctAnswer": "130",
      "diagram": {
        "type": "parallel-transversal-bisector",
        "params": {
          "angle": "80\u00b0"
        }
      },
      "ruleRef": "Qoida 1 & 2: Z-qoidasi va bissektrisa",
      "explanation": "Z-qoidasi bo'yicha $m(\\widehat{CDE}) = 80^\\circ$. $DB$ bissektrisa bo'lgani sababli $m(\\widehat{BDE}) = 40^\\circ$. Ichki bir tomonli burchak orqali $m(\\widehat{ABD}) = 180^\\circ - 50^\\circ = 130^\\circ$."
    }
  ]
};


const TOPIC_2 = {
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



const TOPICS = [TOPIC_1, TOPIC_2];

function getTopicById(id) {
  return TOPICS.find(t => t.id === id) || TOPIC_1;
}

function getAllQuestions() {
  return TOPICS.flatMap(t => t.questions);
}


/**
 * SVG Geometric Diagram Engine
 * Renders crisp, responsive geometric vector diagrams for angle problems
 */

class DiagramRenderer {
  /**
   * Render SVG diagram based on diagram definition
   * @param {Object} diagram - Diagram specification object
   * @returns {string} SVG HTML string
   */
  static render(diagram) {
    if (!diagram || !diagram.type) {
      return '';
    }

    const { type, params = {} } = diagram;

    switch (type) {
      case 'perpendicular-split':
        return this.renderPerpendicularSplit(params);
      case 'multi-bisector-perpendicular':
        return this.renderMultiBisectorPerpendicular(params);
      case 'complete-angle-360':
        return this.renderCompleteAngle360(params);
      case 'parallel-grid-angles':
        return this.renderParallelGrid(params);
      case 'crossed-parallel-angles':
        return this.renderCrossedParallel(params);
      case 'zigzag-opposite-rays':
        return this.renderZigzagOpposite(params);
      case 'triangle-parallel-cut':
        return this.renderTriangleParallelCut(params);
      case 'triangle-exterior-angle':
        return this.renderTriangleExterior(params);
      case 'pencil-head-exterior':
        return this.renderPencilHeadExterior(params);
      case 'multi-zigzag-step':
        return this.renderMultiZigzagStep(params);
      case 'pencil-rule-variables':
      case 'pencil-rule-simple':
      case 'pencil-rule-variable-x':
        return this.renderPencilRule(params);
      case 'triple-parallel-bisector':
        return this.renderTripleParallelBisector(params);
      case 'parallel-triangle-intersection':
        return this.renderParallelTriangle(params);
      case 'parallel-double-bisector':
        return this.renderParallelDoubleBisector(params);
      case 'u-rule-linear':
      case 'u-rule-simple':
        return this.renderURule(params);
      case 'parallel-transversal-bisector':
      case 'z-bisector-split':
        return this.renderZBisector(params);
      case 'supplementary-line':
      case 'supplementary-expr':
        return this.renderSupplementary(params);
      case 'straight-line-3-angles':
        return this.renderStraightLine3Angles(params);
      case 'z-rule-simple':
        return this.renderZRuleSimple(params);
      case 'corresponding-linear':
      case 'transversal-corresponding-supp':
      case 'transversal-supplementary':
        return this.renderTransversal(params);
      case 'm-rule-zigzag':
      case 'm-rule':
        return this.renderMRule(params);
      default:
        return this.renderGenericGeometry(type, params);
    }
  }

  // --- Specialized SVG Builders ---

  static renderPerpendicularSplit(params) {
    const angle1 = params.angle1 || '44°';
    const angle2 = params.angle2 || 'α';
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Perpendicular Right Angle Box -->
        <rect x="180" y="150" width="20" height="20" fill="none" stroke="var(--svg-accent, #eab308)" stroke-width="2" />
        <circle cx="190" cy="160" r="2.5" fill="var(--svg-accent, #eab308)" />

        <!-- Base Line A-B-C -->
        <line x1="40" y1="170" x2="320" y2="170" stroke="var(--svg-line-color, #94a3b8)" stroke-width="2.5" marker-end="url(#arrow)" marker-start="url(#arrow)" />
        
        <!-- Perpendicular Ray BE -->
        <line x1="180" y1="170" x2="180" y2="40" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" />
        
        <!-- Dividing Ray BD -->
        <line x1="180" y1="170" x2="270" y2="80" stroke="var(--svg-ray-color, #f43f5e)" stroke-width="2.5" marker-end="url(#arrow)" />

        <!-- Angle Arcs -->
        <path d="M 180 130 A 40 40 0 0 1 208 142" fill="none" stroke="var(--svg-angle-1, #38bdf8)" stroke-width="2" />
        <path d="M 215 147 A 50 50 0 0 1 230 170" fill="none" stroke="var(--svg-angle-2, #ec4899)" stroke-width="2" />

        <!-- Labels -->
        <text x="30" y="175" class="svg-label">A</text>
        <text x="180" y="195" class="svg-label">B</text>
        <text x="330" y="175" class="svg-label">C</text>
        <text x="175" y="30" class="svg-label">E</text>
        <text x="280" y="75" class="svg-label">D</text>

        <text x="185" y="125" class="svg-angle-val" fill="#38bdf8">${angle1}</text>
        <text x="235" y="155" class="svg-angle-val highlight" fill="#ec4899">${angle2}</text>
      </svg>
    `;
  }

  static renderZRuleSimple(params) {
    const angle = params.angle || '70°';
    const target = params.target || 'α';
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Parallel line d1 -->
        <line x1="40" y1="60" x2="320" y2="60" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" marker-start="url(#arrow)" />
        <text x="330" y="65" class="svg-label">d₁</text>

        <!-- Parallel line d2 -->
        <line x1="40" y1="160" x2="320" y2="160" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" marker-start="url(#arrow)" />
        <text x="330" y="165" class="svg-label">d₂</text>

        <!-- Transversal transversal BC -->
        <line x1="120" y1="60" x2="240" y2="160" stroke="var(--svg-ray-color, #f43f5e)" stroke-width="2.5" />

        <!-- Angle Arcs -->
        <path d="M 150 60 A 30 30 0 0 1 144 80" fill="none" stroke="var(--svg-angle-1, #38bdf8)" stroke-width="2" />
        <path d="M 210 160 A 30 30 0 0 1 216 140" fill="none" stroke="var(--svg-angle-2, #ec4899)" stroke-width="2" />

        <!-- Labels -->
        <text x="110" y="50" class="svg-label">B</text>
        <text x="245" y="180" class="svg-label">C</text>
        <text x="155" y="85" class="svg-angle-val" fill="#38bdf8">${angle}</text>
        <text x="190" y="150" class="svg-angle-val highlight" fill="#ec4899">${target}</text>
      </svg>
    `;
  }

  static renderURule(params) {
    const angle1 = params.expr1 || params.angle || '55°';
    const angle2 = params.expr2 || params.target || 'α';
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Parallel line d1 -->
        <line x1="40" y1="60" x2="320" y2="60" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" marker-start="url(#arrow)" />
        <text x="330" y="65" class="svg-label">d₁</text>

        <!-- Parallel line d2 -->
        <line x1="40" y1="160" x2="320" y2="160" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" marker-start="url(#arrow)" />
        <text x="330" y="165" class="svg-label">d₂</text>

        <!-- Transversal line -->
        <line x1="220" y1="60" x2="140" y2="160" stroke="var(--svg-ray-color, #f43f5e)" stroke-width="2.5" />

        <!-- Inner Angles (U-shape) -->
        <path d="M 195 60 A 25 25 0 0 1 200 85" fill="none" stroke="var(--svg-angle-1, #38bdf8)" stroke-width="2" />
        <path d="M 165 160 A 25 25 0 0 0 160 135" fill="none" stroke="var(--svg-angle-2, #ec4899)" stroke-width="2" />

        <text x="225" y="50" class="svg-label">B</text>
        <text x="130" y="180" class="svg-label">C</text>
        <text x="175" y="85" class="svg-angle-val" fill="#38bdf8">${angle1}</text>
        <text x="175" y="145" class="svg-angle-val highlight" fill="#ec4899">${angle2}</text>
      </svg>
    `;
  }

  static renderPencilRule(params) {
    const b1 = params.b1 || params.a1 || '150°';
    const b2 = params.b2 || params.a2 || '100°';
    const b3 = params.b3 || params.target || 'α';
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Top Parallel line -->
        <line x1="60" y1="50" x2="300" y2="50" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="310" y="55" class="svg-label">d₁</text>

        <!-- Bottom Parallel line -->
        <line x1="60" y1="170" x2="300" y2="170" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="310" y="175" class="svg-label">d₂</text>

        <!-- Siniq chiziq (Pencil point) -->
        <polyline points="100,50 60,110 120,170" fill="none" stroke="var(--svg-ray-color, #f43f5e)" stroke-width="2.5" />

        <!-- Angle arcs -->
        <path d="M 100 50 A 25 25 0 0 1 80 80" fill="none" stroke="#38bdf8" stroke-width="2" />
        <path d="M 75 90 A 25 25 0 0 1 85 135" fill="none" stroke="#eab308" stroke-width="2" />
        <path d="M 100 170 A 25 25 0 0 0 90 145" fill="none" stroke="#ec4899" stroke-width="2" />

        <text x="110" y="75" class="svg-angle-val" fill="#38bdf8">${b1}</text>
        <text x="95" y="115" class="svg-angle-val" fill="#eab308">${b2}</text>
        <text x="125" y="155" class="svg-angle-val highlight" fill="#ec4899">${b3}</text>
      </svg>
    `;
  }

  static renderMRule(params) {
    const a1 = params.a1 || '135°';
    const a2 = params.a2 || '75°';
    const target = params.target || 'α';
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Top line -->
        <line x1="50" y1="50" x2="310" y2="50" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="320" y="55" class="svg-label">d₁</text>

        <!-- Bottom line -->
        <line x1="50" y1="170" x2="310" y2="170" stroke="var(--svg-line-color, #38bdf8)" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="320" y="175" class="svg-label">d₂</text>

        <!-- Zigzag M -->
        <polyline points="200,50 120,110 210,170" fill="none" stroke="var(--svg-ray-color, #f43f5e)" stroke-width="2.5" />

        <text x="210" y="40" class="svg-label">B</text>
        <text x="100" y="115" class="svg-label">C</text>
        <text x="220" y="180" class="svg-label">D</text>

        <text x="170" y="75" class="svg-angle-val" fill="#38bdf8">${a1}</text>
        <text x="135" y="115" class="svg-angle-val highlight" fill="#ec4899">${target}</text>
        <text x="175" y="155" class="svg-angle-val" fill="#38bdf8">${a2}</text>
      </svg>
    `;
  }

  static renderSupplementary(params) {
    const a1 = params.angle || params.expr1 || '20°';
    const a2 = params.target || params.expr2 || 'α';
    return `
      <svg class="geom-svg" viewBox="0 0 360 200" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Horizontal base line -->
        <line x1="40" y1="140" x2="320" y2="140" stroke="var(--svg-line-color, #94a3b8)" stroke-width="2.5" marker-start="url(#arrow)" marker-end="url(#arrow)" />
        
        <!-- Ray OE -->
        <line x1="180" y1="140" x2="270" y2="50" stroke="var(--svg-ray-color, #f43f5e)" stroke-width="2.5" marker-end="url(#arrow)" />

        <!-- Arcs -->
        <path d="M 140 140 A 40 40 0 0 1 245 75" fill="none" stroke="var(--svg-angle-2, #ec4899)" stroke-width="2" />
        <path d="M 235 85 A 50 50 0 0 1 230 140" fill="none" stroke="var(--svg-angle-1, #38bdf8)" stroke-width="2" />

        <text x="30" y="145" class="svg-label">D</text>
        <text x="180" y="165" class="svg-label">O</text>
        <text x="330" y="145" class="svg-label">F</text>
        <text x="280" y="45" class="svg-label">E</text>

        <text x="150" y="110" class="svg-angle-val highlight" fill="#ec4899">${a2}</text>
        <text x="240" y="125" class="svg-angle-val" fill="#38bdf8">${a1}</text>
      </svg>
    `;
  }

  static renderCompleteAngle360(params) {
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Center O -->
        <circle cx="180" cy="110" r="4" fill="var(--svg-accent, #eab308)" />

        <!-- Rays OA, OB, OC -->
        <line x1="180" y1="110" x2="90" y2="40" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
        <line x1="180" y1="110" x2="290" y2="110" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
        <line x1="180" y1="110" x2="120" y2="190" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#arrow)" />

        <text x="75" y="35" class="svg-label">A</text>
        <text x="300" y="115" class="svg-label">B</text>
        <text x="105" y="205" class="svg-label">C</text>
        <text x="185" y="130" class="svg-label">O</text>

        <!-- Angle values -->
        <text x="150" y="70" class="svg-angle-val" fill="#38bdf8">${params.expr1 || '270 - 2x'}</text>
        <text x="190" y="160" class="svg-angle-val" fill="#38bdf8">${params.expr2 || '2x - 10'}</text>
      </svg>
    `;
  }

  static renderTransversal(params) {
    const a1 = params.expr1 || params.angle || '70°';
    const a2 = params.expr2 || params.target || '3x - 20°';
    return `
      <svg class="geom-svg" viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--svg-line-color, #38bdf8)" />
          </marker>
        </defs>
        <!-- Parallel line d1 -->
        <line x1="40" y1="70" x2="320" y2="70" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="330" y="75" class="svg-label">d₁</text>

        <!-- Parallel line d2 -->
        <line x1="40" y1="160" x2="320" y2="160" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
        <text x="330" y="165" class="svg-label">d₂</text>

        <!-- Transversal line -->
        <line x1="100" y1="20" x2="260" y2="200" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#arrow)" marker-start="url(#arrow)" />

        <text x="175" y="60" class="svg-angle-val" fill="#38bdf8">${a1}</text>
        <text x="245" y="150" class="svg-angle-val highlight" fill="#ec4899">${a2}</text>
      </svg>
    `;
  }

  static renderGenericGeometry(type, params) {
    return `
      <svg class="geom-svg" viewBox="0 0 360 200" xmlns="http://www.w3.org/2000/svg">
        <rect width="360" height="200" rx="12" fill="rgba(56, 189, 248, 0.05)" />
        <!-- Generic Geometry Lines -->
        <line x1="40" y1="60" x2="320" y2="60" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4" />
        <line x1="40" y1="140" x2="320" y2="140" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4" />
        <polyline points="80,60 180,100 280,140" fill="none" stroke="#f43f5e" stroke-width="2.5" />
        <text x="180" y="110" text-anchor="middle" class="svg-label">Geometrik Masala Chizmasi</text>
      </svg>
    `;
  }

  // Fallback helper methods for remaining types
  static renderMultiBisectorPerpendicular(p) { return this.renderPerpendicularSplit({ angle1: '30°', angle2: 'y' }); }
  static renderParallelGrid(p) { return this.renderZRuleSimple({ angle: '40°', target: '20°' }); }
  static renderCrossedParallel(p) { return this.renderURule({ expr1: 'x - 55°', expr2: '2x + 10°' }); }
  static renderZigzagOpposite(p) { return this.renderMRule({ a1: '110°', a2: '20°', target: 'α' }); }
  static renderTriangleParallelCut(p) { return this.renderZRuleSimple({ angle: '70°', target: '80°' }); }
  static renderTriangleExterior(p) { return this.renderZRuleSimple({ angle: '15°', target: '65°' }); }
  static renderPencilHeadExterior(p) { return this.renderPencilRule({ a1: '70°', a2: '175°', target: 'α' }); }
  static renderMultiZigzagStep(p) { return this.renderMRule({ a1: '110°', a2: '60°', target: 'α' }); }
  static renderTripleParallelBisector(p) { return this.renderPencilRule({ a1: '100°', a2: '110°', target: 'α' }); }
  static renderParallelTriangle(p) { return this.renderZRuleSimple({ angle: '50°', target: '110°' }); }
  static renderParallelDoubleBisector(p) { return this.renderPencilRule({ a1: '150°', a2: 'α', target: '150°' }); }
  static renderZBisector(p) { return this.renderZRuleSimple({ angle: '80°', target: 'α' }); }
  static renderStraightLine3Angles(p) { return this.renderSupplementary({ angle: '40° + 40°', target: 'α' }); }
}




class QuizEngine {
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




class FormulaEngine {
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

  



function startApp() {
  if (!window.app) {
    window.app = new QuizApp();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startApp);
} else {
  startApp();
}

})();
