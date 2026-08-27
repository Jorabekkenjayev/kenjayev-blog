/**
 * Puza Geometri - Burchaklar: 10 Fundamental Qoidalar va Formulalar Bazasi
 */
export const ALL_RULES = [
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
