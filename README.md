# Raising-mathieu-lambert

## 1. Objective
The goal of this project is to implement the main features of an application using the techniques covered in previous sessions. The information provided here is intentionally brief. Please refer to the resources from previous sessions for additional guidance.

---

## 2. Application Description
We will create an application that simulates a **rabbit farming management game**. This is a turn-based strategy game, focusing on decision-making and resource management. Players are given limited resources, encouraging them to think strategically about their optimal use.

### Resources to Manage:
- **Number of rabbits**: males, females, reproduction, and sales.
- **Amount of food**.
- **Number of cages**.
- **Cash balance**.

### Gameplay:
1. **Initialization**:  
   Players will start by setting the initial parameters of the game, such as the starting quantities of the various resources.

2. **Player Actions**:  
   Each turn, players can:
   - Sell rabbits.
   - Purchase consumables.  
   Once their actions are complete, they will indicate the end of their turn.

3. **Time Progression**:  
   The application will then advance time by one month and apply internal rules based on the following mechanics:

---

### Game Rules:
#### Reproduction:
- Female rabbits reach maturity and can reproduce at **6 months old**.
- They can continue giving birth for **4 years**.
- Gestation lasts **1 month**, and each litter can produce **1 to 4 kits**.
- A female can become pregnant again a few days after giving birth.

#### Growth:
- A rabbit reaches adulthood at **3 months old**.

#### Feeding:
- An adult rabbit consumes **250 g/day**.
- A kit consumes:
  - **Mother's milk** (free) during the 1st month.
  - **100 g/day** during the 2nd month.
  - **250 g/day** starting from the 3rd month.
- If a rabbit lacks food for a month, it **dies**.

#### Cages:
- A cage can hold up to **6 rabbits**.
- Overcrowding occurs when there are **10 or more rabbits per cage**, increasing the risk of disease and causing **deaths**.
- Kits (less than 1 month old) do not count toward overcrowding.

---
