# Display Manufacturing Quick Reference

## Manufacturing Overview
Display manufacturing combines semiconductor, materials, and optical technologies in highly controlled cleanroom environments.

## Substrate Preparation
**Materials:** Glass, polyimide, metal foil  
**Sizes:** Gen 4 (730×920mm) to Gen 10.5 (2940×3370mm)  
**Process Steps:**
1. **Cleaning** - Remove particles and organic contamination
2. **Surface Treatment** - Improve adhesion and uniformity  
3. **Inspection** - Defect detection and classification

### Glass Substrate Types
- **Soda-lime Glass** - Low cost, standard applications
- **Borosilicate** - Better thermal stability  
- **Aluminosilicate** - High-end applications
- **Alkali-free** - Semiconductor compatibility

---

## Thin Film Deposition
**Purpose:** Create functional layers (conductors, semiconductors, insulators)  
**Methods:** Sputtering, CVD, evaporation, coating

### Common Materials
| Layer Type | Materials | Thickness | Method |
|------------|-----------|-----------|---------|
| Gate Metal | Mo, Al, Cu | 200-500nm | Sputtering |
| Gate Insulator | SiO₂, SiNₓ | 200-400nm | PECVD |
| Semiconductor | a-Si, LTPS | 50-200nm | PECVD/Laser |
| Source/Drain | Mo, Al | 200-500nm | Sputtering |
| Passivation | SiNₓ, SiO₂ | 200-400nm | PECVD |

### Deposition Methods
- **Sputtering** - Physical vapor deposition, good uniformity
- **CVD** - Chemical vapor deposition, conformal coverage  
- **Evaporation** - Thermal/e-beam, organic materials
- **Coating** - Spin/slot-die, polymers and solutions

---

## Photolithography
**Purpose:** Pattern transfer from masks to substrates  
**Resolution:** 2-10μm typical for displays  
**Equipment:** Stepper, scanner, contact aligner

### Process Steps
1. **Resist Coating** - Photoresist application
2. **Pre-bake** - Solvent removal, adhesion
3. **Exposure** - UV light through mask
4. **Post-bake** - Chemical amplification
5. **Development** - Resist removal
6. **Inspection** - Critical dimension check

### Key Parameters
- **Resolution** - Minimum feature size
- **Overlay** - Layer-to-layer alignment accuracy
- **CD Control** - Critical dimension uniformity
- **Defectivity** - Particle and defect levels

---

## Etching Processes
**Purpose:** Remove unwanted material selectively  
**Types:** Wet chemical, dry plasma

### Wet Etching
- **Advantages** - Simple, low cost, high selectivity
- **Disadvantages** - Isotropic, limited resolution  
- **Applications** - ITO patterning, organic materials

### Dry Etching (Plasma)
- **Advantages** - Anisotropic, precise control
- **Disadvantages** - Equipment cost, damage risk
- **Applications** - Silicon etching, metal patterning

---

## TFT Array Process
**Typical Mask Count:** 4-6 masks  
**Key Process:** Gate → G.I. → a-Si → S/D → Passivation → Contact

### TFT Types and Processes
| TFT Type | Process Temp | Mobility | Applications |
|----------|--------------|----------|-------------|
| a-Si | <350°C | 0.5-1 cm²/V·s | Large displays |
| LTPS | 400-600°C | 50-100 cm²/V·s | Mobile, small |
| IGZO | <350°C | 10-50 cm²/V·s | Large, high-res |
| Oxide | <400°C | 10-30 cm²/V·s | Flexible |

---

## Color Filter Manufacturing
**Purpose:** Create RGB color selection  
**Methods:** Pigment dispersion, dye-based, quantum dot

### Process Flow
1. **Black Matrix** - Define pixel boundaries
2. **Red Filter** - Photoresist + red pigment
3. **Green Filter** - Photoresist + green pigment  
4. **Blue Filter** - Photoresist + blue pigment
5. **Overcoat** - Planarization layer
6. **ITO Coating** - Common electrode

### Color Filter Types
- **RGB Stripe** - Equal subpixel sizes
- **PenTile** - Shared subpixels, fewer green
- **RGBW** - White subpixel for brightness
- **Quantum Dot** - Blue excitation, QD conversion

---

## Cell Assembly
**Purpose:** Combine TFT array and color filter  
**Process:** Alignment, sealing, liquid crystal injection

### LCD Assembly Steps
1. **Sealant Dispensing** - UV-curable adhesive
2. **Spacer Distribution** - Control cell gap
3. **Panel Bonding** - Pressure and UV cure
4. **Liquid Crystal Fill** - Vacuum injection
5. **End Seal** - Close injection port

### Critical Parameters
- **Cell Gap** - Liquid crystal thickness (2-5μm)
- **Alignment** - Rubbing or photoalignment
- **Uniformity** - Spacer distribution
- **Contamination** - Particle control

---

## OLED Manufacturing
**Key Challenges:** Moisture sensitivity, organic material handling  
**Environment:** Ultra-low moisture (<1ppm)

### OLED Stack Structure
1. **TFT Backplane** - Pixel driving circuits
2. **Planarization** - Smooth surface
3. **Anode** - ITO or metal
4. **Organic Layers** - HIL/HTL/EML/ETL/EIL
5. **Cathode** - Metal electrode
6. **Encapsulation** - Moisture barrier

### Deposition Methods
- **Thermal Evaporation** - Small molecules, RGB
- **Inkjet Printing** - Solution-based, polymers  
- **Slot-die Coating** - Large area coating
- **Laser Transfer** - Micro OLED applications

---

## Quality Control
**Inline Testing:** Each process step monitoring  
**Final Testing:** Complete panel characterization

### Key Measurements
- **Optical** - Brightness, uniformity, color
- **Electrical** - TFT characteristics, leakage
- **Visual** - Mura, defects, cosmetic issues
- **Reliability** - Lifetime, environmental testing

### Defect Types
- **Point Defects** - Bright/dark pixels
- **Line Defects** - Row/column failures  
- **Area Defects** - Large region issues
- **Mura** - Brightness non-uniformity

---

## Yield Management
**Definition:** Percentage of good panels from total production  
**Target:** >90% for mature processes

### Yield Loss Sources
- **Particle Contamination** - Cleanroom control critical
- **Process Variation** - Equipment and material consistency
- **Mask Defects** - Pattern transfer issues
- **Material Defects** - Substrate and chemical quality

### Improvement Strategies
- **Statistical Process Control** - Real-time monitoring
- **Defect Source Analysis** - Root cause identification
- **Process Optimization** - Parameter tuning
- **Equipment Maintenance** - Preventive care

---

## Environmental and Safety
**Chemicals:** Acids, solvents, dopants, metals  
**Gases:** Silane, ammonia, hydrogen, chlorine  
**Safety Systems:** Ventilation, gas monitoring, emergency response

### Waste Management
- **Chemical Waste** - Treatment and disposal
- **Substrate Scrap** - Recycling programs  
- **Water Treatment** - Purification and reuse
- **Air Emissions** - Scrubbing and monitoring

---

## Cost Structure
**Major Cost Elements:**
- Materials (40-50%): Substrate, chemicals, targets
- Equipment (20-30%): Depreciation, maintenance  
- Labor (10-15%): Operators, engineers, support
- Utilities (10-15%): Power, gases, water
- Overhead (5-10%): Facilities, administration

### Cost Reduction Strategies
- **Larger Substrates** - Economy of scale
- **Higher Yields** - Fewer defective panels
- **Process Integration** - Fewer steps
- **Material Efficiency** - Reduced waste