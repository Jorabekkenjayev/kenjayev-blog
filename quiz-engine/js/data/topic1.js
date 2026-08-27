export const TOPIC_1 = {
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
