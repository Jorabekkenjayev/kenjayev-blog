/**
 * SVG Geometric Diagram Engine
 * Renders crisp, responsive geometric vector diagrams for angle problems
 */

export class DiagramRenderer {
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
