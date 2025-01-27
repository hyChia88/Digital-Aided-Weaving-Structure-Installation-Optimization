# Weaving-Structure-Installation-Optimization-and-Automated
**Author:** Chia Hui Yen  
**Mentor:** Professor Huang Weixin  
**Coordinator:** Mr. Wei from Hebei Lu Cheng Machinery Co.  
**Date:** 2024 Spring  
**Files:** grasshopper files and C++ program to transmit signal data between electronic components

## About the Project

This library contains the code for a Label Machine Control App, developed as part of the research project "Digital Aided Installation and Optimization for Weaving Structures". The system automates the labeling of round or rectangular rods (3mm–20mm) with customized codes at specific distances defined by CSV input, significantly improving weaving structure installation efficiency.

## Background: Weaving Structure Installation Challenges

Weaving Structure details can be found in the research paper:  
> Huang, W., Wu, C., Hu, J., & Gao, W. (2022). [Weaving structure: A bending-active gridshell for freeform fabrication](https://doi.org/10.1016/j.autcon.2022.104184). Automation in Construction, 136, 104184.

<p align="center">
<img src="https://github.com/user-attachments/assets/02b4bc96-e3de-4e11-8339-9bc1c4ed72f8" alt="Weaving Structure Example" width="800"/>
</p>

I encountered several challenges during previous installation work, which motivated this research project and the development of an installation aid system.  

<p align="center">
<img src="https://github.com/user-attachments/assets/92a2786a-2804-45dd-9c4b-10282c22f4ce" width="600"/>

- **Challenge (1)**
<img src="https://github.com/user-attachments/assets/e61ee5f0-ae94-47bc-b98b-6d64b8159844" width="800"/>

- **Challenge (2)**
<img src="https://github.com/user-attachments/assets/98342d23-9ebe-4fa8-aee8-b60b8af6780e" width="800"/>
</p>  


## Optimization (1): Optimization of the installation sequences 
### (1) Simulate the Installation Process:
Run simulations to track how structures move and change during installation
![image](https://github.com/user-attachments/assets/a81525ca-91e8-43f2-b83a-287e1f0bd709)

### (2) Analysis of Sequence & Rod Performance
Compare changes in sequence and displacement to understand the basic rules of the process. 
![image](https://github.com/user-attachments/assets/6197931a-54d7-44e3-aabd-e488dbe618e2)

### (3) Generate Installation Guidelines:
Use these rules to create helpful installation sequences for workers.  
![result](https://github.com/user-attachments/assets/4daa9446-d2a5-49bd-a727-becfa8e5ca13)  



## Optimization (2): Development of an automatic rod marking system.  
### **Design Draft**
<img src="https://github.com/user-attachments/assets/22eb9002-d08d-4fe4-802f-878a4dc6f411" alt="Machine Design Draft" width="350"/>
</br>
<img src="https://github.com/user-attachments/assets/86c00e8c-e232-4e80-88c8-eaedc4079a56" alt="process" width="600"/> 


#### Final Machine
<img src="https://github.com/user-attachments/assets/bfffeed1-4324-43eb-ad15-ed9dee3c3e99" alt="Final Machine"/>


## Result Improvement
This application supports custom-designed hardware for automatic rod marking, enabling precise, random-position labeling on weaving rods. The system specifically addresses challenges in manual rod marking for bending-active gridshell structures.  

- **Installation Efficiency**: 33% reduced installation time through improved rod labeling process, enhancing overall efficiency for weaving structure fabrication
- **Enhanced User Experience**: Improved label design with color-coded system for easier rod identification and assembly

### Rod Specifications
<img src="https://github.com/user-attachments/assets/3492cd20-0831-4f46-89f5-f3aa6bb9e6e2" alt="Rod Section" width="400"/>


### Label Design
<img src="https://github.com/user-attachments/assets/b7f1adda-6612-48db-b894-be40f55b5e41" alt="Label Design 1" width="400"/>
<img src="https://github.com/user-attachments/assets/cc4e3a9f-e56c-49d6-84d6-469e8ff6a964" alt="Label Design 2" width="400"/>

### Key Features
- **Precise Labeling:** Millimeter-level precision marking
- **Customizable Positions:** Random distance printing based on project requirements
- **Multi-Color Printing System:**
  - Red: Codes ending in 0-3
  - Blue: Codes ending in 4-6
  - Green: Codes ending in 7-9
- **Versatile Rod Support:** Compatible with various cross-sections (3mm-20mm)
- **CSV Integration:** Automated processing of labeling instructions

<img src="https://github.com/user-attachments/assets/0623a1ea-77a6-4372-9be9-f6a77336d4f6" alt="Final Result" />

## Applications

The system transforms the previously manual task of rod labeling into an automated process, significantly improving the assembly of bending-active gridshell structures. This enhancement provides:
- Automated labeling process
- Improved installation accuracy
- Increased assembly speed
- Reduced human error
